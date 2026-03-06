"""
Handles DICOM, NIfTI, ZIP, image, and PDF inputs.
Converts everything into a NIfTI volume for downstream processing.
"""
import os
import zipfile
import shutil
from pathlib import Path
import numpy as np


def detect_file_type(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".zip":
        return "zip"
    if suffix == ".dcm":
        return "dicom"
    if suffix in (".nii", ".gz"):
        return "nifti"
    if suffix in (".png", ".jpg", ".jpeg"):
        return "image"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".txt":
        return "text"

    # Try reading as DICOM even without extension
    try:
        import pydicom
        pydicom.dcmread(file_path, stop_before_pixels=True)
        return "dicom"
    except Exception:
        pass

    return "unknown"


def extract_zip_dicoms(zip_path: str, extract_dir: str) -> str:
    """Extract ZIP and return directory containing DICOM files."""
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    # Find DICOM files recursively
    dcm_files = list(Path(extract_dir).rglob("*.dcm"))
    if not dcm_files:
        # Try files without extension (common in DICOM exports)
        dcm_files = []
        for f in Path(extract_dir).rglob("*"):
            if f.is_file() and f.suffix == "":
                try:
                    import pydicom
                    pydicom.dcmread(str(f), stop_before_pixels=True)
                    dcm_files.append(f)
                except Exception:
                    pass

    if dcm_files:
        return str(dcm_files[0].parent)
    return extract_dir


def dicom_series_to_nifti(dicom_dir: str, output_path: str) -> str:
    """Convert a DICOM series directory to NIfTI."""
    import SimpleITK as sitk

    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(dicom_dir)

    if not series_ids:
        raise ValueError(f"No DICOM series found in {dicom_dir}")

    # Use the first series (largest by file count)
    best_series = series_ids[0]
    for sid in series_ids:
        files = reader.GetGDCMSeriesFileNames(dicom_dir, sid)
        best_files = reader.GetGDCMSeriesFileNames(dicom_dir, best_series)
        if len(files) > len(best_files):
            best_series = sid

    file_names = reader.GetGDCMSeriesFileNames(dicom_dir, best_series)
    reader.SetFileNames(file_names)
    image = reader.Execute()
    sitk.WriteImage(image, output_path)
    return output_path


def single_dicom_to_nifti(dicom_path: str, output_path: str) -> str:
    """Convert a single DICOM file to NIfTI."""
    import SimpleITK as sitk

    image = sitk.ReadImage(dicom_path)
    sitk.WriteImage(image, output_path)
    return output_path


def image_to_nifti(image_path: str, output_path: str) -> str:
    """Convert a 2D PNG/JPG to a single-slice NIfTI (grayscale)."""
    import SimpleITK as sitk
    from PIL import Image

    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.int16)
    arr = arr[:, :, np.newaxis]  # Add Z dimension

    sitk_image = sitk.GetImageFromArray(arr.transpose(2, 1, 0))
    sitk_image.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(sitk_image, output_path)
    return output_path


def convert_to_nifti(file_path: str, output_path: str, file_type: str, extract_dir: str = None) -> str:
    """Universal converter - returns path to NIfTI file."""
    if file_type == "nifti":
        shutil.copy(file_path, output_path)
        return output_path

    if file_type == "dicom":
        # Check if it's a directory of DICOMs
        p = Path(file_path)
        if p.is_dir():
            return dicom_series_to_nifti(file_path, output_path)
        else:
            # Single file - try as series from parent dir
            try:
                return dicom_series_to_nifti(str(p.parent), output_path)
            except Exception:
                return single_dicom_to_nifti(file_path, output_path)

    if file_type == "zip":
        if extract_dir is None:
            extract_dir = str(Path(file_path).parent / "extracted")
        dicom_dir = extract_zip_dicoms(file_path, extract_dir)
        return dicom_series_to_nifti(dicom_dir, output_path)

    if file_type == "image":
        return image_to_nifti(file_path, output_path)

    raise ValueError(f"Cannot convert file type: {file_type}")


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF report."""
    try:
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"[PDF extraction failed: {e}]"
