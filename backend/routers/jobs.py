from fastapi import APIRouter, HTTPException
from workers.tasks import get_job

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Poll job status and result."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found")
    return job


@router.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    """Get the final result of a completed job."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found")
    if job["status"] != "completed":
        raise HTTPException(400, f"Job is not completed (status: {job['status']})")
    return job["result"]
