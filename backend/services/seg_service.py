"""
Segmentation service.
Primary: TotalSegmentator (auto-segments 104 anatomical structures).
Fallback: SimpleITK threshold segmentation (works on any machine, no GPU needed).
"""
import os
import numpy as np
from pathlib import Path


# Structures to segment and their display colors (RGB 0-255)
STRUCTURE_COLORS = {
    "lung_left":        [0, 220, 80],
    "lung_right":       [0, 200, 100],
    "liver":            [200, 100, 50],
    "spleen":           [180, 60, 180],
    "kidney_left":      [220, 80, 80],
    "kidney_right":     [200, 60, 60],
    "heart":            [240, 50, 50],
    "aorta":            [240, 100, 30],
    "trachea":          [100, 180, 240],
    "femur_left":       [240, 200, 100],
    "femur_right":      [230, 190, 90],
    "vertebrae_L1":     [180, 160, 140],
    "vertebrae_T1":     [170, 150, 130],
    "tumor_mass":       [200, 0, 200],
    "brain":            [220, 180, 140],
}


def run_totalsegmentator(nifti_path: str, output_dir: str) -> dict:
    """Run TotalSegmentator for full-body auto-segmentation."""
    from totalsegmentator.python_api import totalsegmentator

    os.makedirs(output_dir, exist_ok=True)
    totalsegmentator(
        nifti_path,
        output_dir,
        fast=True,         # Fast mode: ~3-5 min CPU, ~30s GPU
        task="total",
        quiet=True,
    )
    # Return available segments
    segments = {}
    for name, color in STRUCTURE_COLORS.items():
        seg_path = os.path.join(output_dir, f"{name}.nii.gz")
        if os.path.exists(seg_path):
            segments[name] = {"path": seg_path, "color": color}
    return segments


def run_threshold_segmentation(nifti_path: str, output_dir: str) -> dict:
    """
    Fallback segmentation using HU thresholds (no AI required).
    Works on CT scans with standard Hounsfield Unit ranges.
    """
    import SimpleITK as sitk
    import nibabel as nib

    os.makedirs(output_dir, exist_ok=True)

    img = nib.load(nifti_path)
    data = img.get_fdata()
    affine = img.affine
    header = img.header

    def save_mask(mask: np.ndarray, name: str) -> str:
        path = os.path.join(output_dir, f"{name}.nii.gz")
        nib_img = nib.Nifti1Image(mask.astype(np.uint8), affine, header)
        nib.save(nib_img, path)
        return path

    def clean_mask(mask, min_size=500):
        """Remove small connected components."""
        from scipy.ndimage import label, binary_fill_holes
        labeled, n = label(mask)
        if n == 0:
            return mask
        sizes = np.bincount(labeled.ravel())
        sizes[0] = 0
        largest = sizes.argmax()
        return (labeled == largest).astype(np.uint8)

    segments = {}

    # CT scan ranges (Hounsfield Units)
    hu_min = data.min()
    found_any = False

    # Bone: HU 400-1900
    if hu_min < -100:  # Looks like a proper CT
        bone_mask = ((data >= 400) & (data <= 1900)).astype(np.uint8)
        if bone_mask.sum() > 10:
            path = save_mask(bone_mask, "bone")
            segments["bone"] = {"path": path, "color": [240, 220, 160]}
            found_any = True

        # Lung: HU -950 to -400
        lung_mask = ((data >= -950) & (data <= -400)).astype(np.uint8)
        if lung_mask.sum() > 10:
            lung_clean = clean_mask(lung_mask)
            path = save_mask(lung_clean, "lung_left")
            segments["lung_left"] = {"path": path, "color": [0, 220, 80]}
            found_any = True

        # Soft tissue: HU 0-100
        soft_mask = ((data >= 0) & (data <= 100)).astype(np.uint8)
        if soft_mask.sum() > 10:
            path = save_mask(soft_mask, "soft_tissue")
            segments["soft_tissue"] = {"path": path, "color": [200, 150, 100]}
            found_any = True

    if not found_any:
        # MRI, single-slice DCM, or CT with no usable HU ranges: use Otsu thresholding
        import SimpleITK as sitk
        sitk_img = sitk.ReadImage(nifti_path)
        otsu = sitk.OtsuThresholdImageFilter()
        otsu.SetInsideValue(0)
        otsu.SetOutsideValue(1)
        mask_sitk = otsu.Execute(sitk_img)
        mask_arr = sitk.GetArrayFromImage(mask_sitk)
        path = save_mask(mask_arr.transpose(2, 1, 0), "tissue")
        segments["tissue"] = {"path": path, "color": [150, 180, 220]}

    return segments


def run_segmentation(nifti_path: str, output_dir: str) -> dict:
    """Try TotalSegmentator first, fall back to threshold segmentation."""
    try:
        import totalsegmentator  # noqa
        print("[Segmentation] Using TotalSegmentator")
        return run_totalsegmentator(nifti_path, output_dir)
    except ImportError:
        print("[Segmentation] TotalSegmentator not installed, using threshold fallback")
        return run_threshold_segmentation(nifti_path, output_dir)
    except Exception as e:
        print(f"[Segmentation] TotalSegmentator failed ({e}), using threshold fallback")
        return run_threshold_segmentation(nifti_path, output_dir)
