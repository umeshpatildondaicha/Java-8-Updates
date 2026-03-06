from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import settings
from services.llm_service import parse_report_text

router = APIRouter()


class ReportParseRequest(BaseModel):
    text: str


@router.post("/reports/parse")
def parse_report(req: ReportParseRequest):
    """
    Parse a radiology report text directly (no file upload needed).
    Returns structured JSON findings.
    """
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            503,
            "ANTHROPIC_API_KEY not configured. Add it to your .env file."
        )
    if len(req.text.strip()) < 10:
        raise HTTPException(400, "Report text is too short")

    result = parse_report_text(req.text, settings.ANTHROPIC_API_KEY)
    return result
