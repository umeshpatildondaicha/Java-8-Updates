"""
Converts NIfTI segmentation masks into 3D GLB meshes for web viewing.
Uses Marching Cubes (via PyVista) + mesh smoothing + decimation.
"""
import os
import numpy as np
from pathlib import Path


def nifti_mask_to_glb(nifti_path: str, output_glb: str, color_rgb: list) -> str | None:
    """
    Convert a binary NIfTI mask to a smoothed GLB mesh.

    Args:
        nifti_path: Path to binary NIfTI mask file
        output_glb: Output GLB file path
        color_rgb: [R, G, B] color values 0-255

    Returns:
        output_glb path if successful, None if mask is empty
    """
    try:
        import nibabel as nib
        import pyvista as pv
        import trimesh

        img = nib.load(nifti_path)
        data = img.get_fdata()

        if data.sum() < 10:
            return None

        # Get voxel spacing for physical coordinates
        spacing = tuple(float(s) for s in img.header.get_zooms()[:3])
        if any(s <= 0 for s in spacing):
            spacing = (1.0, 1.0, 1.0)

        # Build PyVista ImageData with correct spacing
        grid = pv.ImageData()
        grid.dimensions = np.array(data.shape) + 1  # cell → point conversion
        grid.spacing = spacing
        grid.origin = (0.0, 0.0, 0.0)
        grid.cell_data["values"] = data.flatten(order="F").astype(np.float32)

        # Marching cubes at threshold 0.5
        mesh = grid.threshold(0.5)
        if mesh.n_points == 0:
            return None

        surface = mesh.extract_surface()

        # Smooth & decimate for web performance
        surface = surface.smooth(n_iter=50, relaxation_factor=0.1)
        target_faces = min(50_000, surface.n_faces)
        if surface.n_faces > target_faces:
            ratio = 1.0 - (target_faces / surface.n_faces)
            surface = surface.decimate(ratio)

        # Convert to trimesh for GLB export
        vertices = np.array(surface.points, dtype=np.float32)
        faces_flat = np.array(surface.faces)
        faces = faces_flat.reshape(-1, 4)[:, 1:4]

        tm = trimesh.Trimesh(vertices=vertices, faces=faces)
        tm.visual = trimesh.visual.ColorVisuals(
            mesh=tm,
            vertex_colors=np.array(
                [[color_rgb[0], color_rgb[1], color_rgb[2], 200]] * len(vertices),
                dtype=np.uint8,
            ),
        )

        os.makedirs(os.path.dirname(output_glb), exist_ok=True)
        tm.export(output_glb)
        return output_glb

    except Exception as e:
        print(f"[MeshService] Failed to convert {nifti_path}: {e}")
        return None


def generate_meshes(seg_dir: str, output_dir: str, segments: dict = None) -> list:
    """
    Generate GLB meshes for all segmented structures.

    Args:
        seg_dir: Directory containing NIfTI segmentation masks
        output_dir: Directory to write GLB files
        segments: Dict of {name: {path, color}} from seg_service

    Returns:
        List of {name, filename, color, url_path} dicts
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    if segments is None:
        # Auto-discover NIfTI files in seg_dir
        from services.seg_service import STRUCTURE_COLORS
        segments = {}
        for f in Path(seg_dir).glob("*.nii.gz"):
            name = f.stem.replace(".nii", "")
            color = STRUCTURE_COLORS.get(name, [150, 150, 200])
            segments[name] = {"path": str(f), "color": color}

    for name, info in segments.items():
        glb_filename = f"{name}.glb"
        glb_path = os.path.join(output_dir, glb_filename)

        result = nifti_mask_to_glb(info["path"], glb_path, info["color"])
        if result:
            results.append({
                "name": name,
                "filename": glb_filename,
                "color": info["color"],
            })
            print(f"[MeshService] Generated mesh: {name}")
        else:
            print(f"[MeshService] Skipped empty mask: {name}")

    return results


def generate_volume_preview(nifti_path: str, output_dir: str) -> dict:
    """
    Generate axial/sagittal/coronal PNG slices for quick preview
    before the full 3D viewer loads.
    """
    try:
        import nibabel as nib
        from PIL import Image

        os.makedirs(output_dir, exist_ok=True)
        img = nib.load(nifti_path)
        data = img.get_fdata()

        # Normalize to 0-255
        dmin, dmax = data.min(), data.max()
        if dmax > dmin:
            norm = ((data - dmin) / (dmax - dmin) * 255).astype(np.uint8)
        else:
            norm = np.zeros_like(data, dtype=np.uint8)

        slices = {
            "axial":    norm[:, :, data.shape[2] // 2],
            "sagittal": norm[data.shape[0] // 2, :, :],
            "coronal":  norm[:, data.shape[1] // 2, :],
        }

        previews = {}
        for view, arr in slices.items():
            img_pil = Image.fromarray(arr.T if view != "axial" else arr)
            img_pil = img_pil.rotate(90, expand=True)
            out_path = os.path.join(output_dir, f"preview_{view}.png")
            img_pil.save(out_path)
            previews[view] = out_path

        return previews

    except Exception as e:
        print(f"[MeshService] Preview generation failed: {e}")
        return {}
