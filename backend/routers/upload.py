import uuid
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from config import settings
from workers.tasks import update_job, process_medical_file

router = APIRouter()

MAX_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024
ALLOWED = {".dcm", ".nii", ".gz", ".png", ".jpg", ".jpeg", ".pdf", ".txt", ".zip"}


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    report_text: str = Form(default=""),
):
    """
    Upload a medical file for processing.
    Accepts: DICOM, NIfTI, ZIP (of DICOMs), PNG/JPG (X-ray), PDF, TXT reports.
    Optionally include a radiology report text alongside the scan.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(400, f"File type '{suffix}' not supported. Allowed: {sorted(ALLOWED)}")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"File too large. Maximum size: {settings.MAX_UPLOAD_MB} MB")

    job_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Create initial job record
    update_job(job_id, "queued", 0, "File uploaded, waiting to process...")

    # Start async processing
    background_tasks.add_task(
        process_medical_file,
        job_id,
        str(file_path),
        report_text,
    )

    return {
        "job_id": job_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "status": "queued",
        "message": "File uploaded. Processing started.",
    }


@router.post("/upload/report-text")
async def upload_report_text(
    background_tasks: BackgroundTasks,
    report_text: str = Form(...),
):
    """Upload a plain-text radiology report for AI parsing (no scan needed)."""
    if len(report_text.strip()) < 20:
        raise HTTPException(400, "Report text is too short")

    job_id = str(uuid.uuid4())

    # Save text to a temp file
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / "report.txt"
    with open(file_path, "w") as f:
        f.write(report_text)

    update_job(job_id, "queued", 0, "Report received...")
    background_tasks.add_task(process_medical_file, job_id, str(file_path))

    return {"job_id": job_id, "status": "queued"}
