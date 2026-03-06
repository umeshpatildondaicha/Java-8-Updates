"""
Background processing pipeline for medical files.
Runs in FastAPI BackgroundTasks (no Celery needed for MVP).
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from config import settings
from services.dicom_service import (
    detect_file_type,
    convert_to_nifti,
    extract_pdf_text,
)
from services.seg_service import run_segmentation
from services.mesh_service import generate_meshes, generate_volume_preview
from services.llm_service import parse_report_text, analyze_medical_image


def update_job(job_id: str, status: str, progress: int = 0,
               message: str = "", result: dict = None, error: str = None):
    """Write job state to a JSON file in the output directory."""
    job_dir = Path(settings.OUTPUT_DIR) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    state = {
        "job_id": job_id,
        "status": status,          # queued | processing | completed | failed
        "progress": progress,       # 0-100
        "message": message,
        "result": result or {},
        "error": error,
        "updated_at": datetime.utcnow().isoformat(),
    }
    with open(job_dir / "job.json", "w") as f:
        json.dump(state, f, indent=2)


def get_job(job_id: str) -> dict | None:
    job_file = Path(settings.OUTPUT_DIR) / job_id / "job.json"
    if not job_file.exists():
        return None
    with open(job_file) as f:
        return json.load(f)


def process_medical_file(job_id: str, file_path: str, report_text: str = ""):
    """
    Main pipeline:
      DICOM/NIfTI/ZIP  →  NIfTI  →  Segmentation  →  Meshes  →  result
      Image (X-ray)    →  Claude vision analysis    →  result
      PDF/Text report  →  Claude text analysis      →  result
    """
    output_dir = Path(settings.OUTPUT_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        update_job(job_id, "processing", 5, "Detecting file type...")
        file_type = detect_file_type(file_path)
        print(f"[Job {job_id}] File type: {file_type} | Path: {file_path}")

        # ── 3D Volumetric: CT / MRI ──────────────────────────────────────────
        if file_type in ("dicom", "nifti", "zip"):
            update_job(job_id, "processing", 15, "Converting to NIfTI volume...")
            nifti_path = str(output_dir / "volume.nii.gz")
            extract_dir = str(output_dir / "extracted")
            convert_to_nifti(file_path, nifti_path, file_type, extract_dir)

            update_job(job_id, "processing", 35, "Generating 2D slice previews...")
            previews = generate_volume_preview(nifti_path, str(output_dir / "previews"))

            update_job(job_id, "processing", 45, "Running AI segmentation (may take a few minutes)...")
            seg_dir = str(output_dir / "segmentation")
            segments = run_segmentation(nifti_path, seg_dir)

            update_job(job_id, "processing", 75, f"Generating 3D meshes for {len(segments)} structures...")
            meshes = generate_meshes(seg_dir, str(output_dir / "meshes"), segments)

            # Parse accompanying report if provided
            report_data = {}
            if report_text and settings.ANTHROPIC_API_KEY:
                update_job(job_id, "processing", 90, "Parsing radiology report with AI...")
                report_data = parse_report_text(report_text, settings.ANTHROPIC_API_KEY)

            result = {
                "type": "3d",
                "volume_url": f"/files/{job_id}/volume.nii.gz",
                "previews": {
                    k: f"/files/{job_id}/previews/{Path(v).name}"
                    for k, v in previews.items()
                },
                "meshes": [
                    {
                        "name": m["name"],
                        "label": m["name"].replace("_", " ").title(),
                        "url": f"/files/{job_id}/meshes/{m['filename']}",
                        "color": m["color"],
                    }
                    for m in meshes
                ],
                "report": report_data,
                "structure_count": len(meshes),
            }
            update_job(job_id, "completed", 100, "Done!", result=result)

        # ── 2D Image: X-ray / Photo ──────────────────────────────────────────
        elif file_type == "image":
            # Copy image to output so it can be served
            ext = Path(file_path).suffix
            out_img = output_dir / f"image{ext}"
            shutil.copy(file_path, out_img)

            report_data = {}
            if settings.ANTHROPIC_API_KEY:
                update_job(job_id, "processing", 40, "Analyzing image with Claude AI vision...")
                report_data = analyze_medical_image(file_path, settings.ANTHROPIC_API_KEY)
            else:
                update_job(job_id, "processing", 40, "No API key — skipping AI analysis")

            result = {
                "type": "2d",
                "image_url": f"/files/{job_id}/image{ext}",
                "report": report_data,
            }
            update_job(job_id, "completed", 100, "Done!", result=result)

        # ── PDF Report ────────────────────────────────────────────────────────
        elif file_type == "pdf":
            update_job(job_id, "processing", 30, "Extracting text from PDF...")
            text = extract_pdf_text(file_path)

            report_data = {}
            if settings.ANTHROPIC_API_KEY:
                update_job(job_id, "processing", 60, "Parsing report with Claude AI...")
                report_data = parse_report_text(text, settings.ANTHROPIC_API_KEY)

            result = {
                "type": "report",
                "raw_text": text[:3000],
                "report": report_data,
            }
            update_job(job_id, "completed", 100, "Done!", result=result)

        # ── Plain Text Report ─────────────────────────────────────────────────
        elif file_type == "text":
            with open(file_path) as f:
                text = f.read()

            report_data = {}
            if settings.ANTHROPIC_API_KEY:
                update_job(job_id, "processing", 50, "Parsing report with Claude AI...")
                report_data = parse_report_text(text, settings.ANTHROPIC_API_KEY)

            result = {
                "type": "report",
                "raw_text": text[:3000],
                "report": report_data,
            }
            update_job(job_id, "completed", 100, "Done!", result=result)

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[Job {job_id}] FAILED:\n{tb}")
        update_job(job_id, "failed", error=str(e))
