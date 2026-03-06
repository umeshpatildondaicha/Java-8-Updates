"""
Claude API integration for:
1. Parsing text/PDF radiology reports into structured JSON
2. Analyzing X-ray/medical images via vision
"""
import json
import re
import base64
from pathlib import Path


REPORT_SYSTEM_PROMPT = """You are a medical AI assistant specializing in radiology report analysis.
Extract structured findings from medical reports. Always return valid JSON only, no other text."""

REPORT_PARSE_PROMPT = """Analyze this medical report and extract structured findings.

Return ONLY a JSON object with this exact structure:
{
  "patient_info": {
    "name": "patient name or 'Unknown'",
    "date": "report date or 'Unknown'",
    "modality": "CT/MRI/X-Ray/PET/Ultrasound/Blood Test/Unknown"
  },
  "findings": [
    {
      "organ": "organ or body part name",
      "finding": "description of what was found",
      "location": "specific anatomical location",
      "size_cm": null or number,
      "severity": "normal/mild/moderate/severe/critical",
      "is_abnormal": true or false,
      "color_hex": "#hex color (green=normal, yellow=mild, orange=moderate, red=severe/critical)"
    }
  ],
  "impression": "overall radiologist impression",
  "recommendation": "recommended follow-up action",
  "urgency": "routine/urgent/critical",
  "language_detected": "English/Hindi/etc"
}

Medical Report:
"""

IMAGE_ANALYSIS_PROMPT = """You are an expert radiologist AI assistant. Analyze this medical image.

Return ONLY a JSON object with this structure:
{
  "patient_info": {
    "name": "Unknown",
    "date": "Unknown",
    "modality": "X-Ray/CT/MRI/etc"
  },
  "image_quality": "good/fair/poor",
  "body_region": "chest/abdomen/brain/spine/extremity/etc",
  "findings": [
    {
      "organ": "organ name",
      "finding": "what you observe",
      "location": "location in image",
      "size_cm": null or estimated size,
      "severity": "normal/mild/moderate/severe/critical",
      "is_abnormal": true or false,
      "color_hex": "#hex color"
    }
  ],
  "impression": "overall assessment",
  "recommendation": "suggested next steps",
  "urgency": "routine/urgent/critical",
  "confidence": "high/medium/low"
}
"""


def parse_report_text(report_text: str, api_key: str) -> dict:
    """Parse a text radiology report using Claude."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=REPORT_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": REPORT_PARSE_PROMPT + report_text,
            }
        ],
    )

    text = response.content[0].text.strip()
    return _extract_json(text)


def analyze_medical_image(image_path: str, api_key: str) -> dict:
    """Analyze a medical image (X-ray, scan photo) using Claude vision."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    suffix = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(suffix, "image/jpeg")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": IMAGE_ANALYSIS_PROMPT,
                    },
                ],
            }
        ],
    )

    text = response.content[0].text.strip()
    return _extract_json(text)


def _extract_json(text: str) -> dict:
    """Robustly extract JSON from LLM response."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code block
    code_block = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding first JSON object
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return error structure
    return {
        "patient_info": {"name": "Unknown", "date": "Unknown", "modality": "Unknown"},
        "findings": [],
        "impression": "Report parsing failed",
        "recommendation": "Please review manually",
        "urgency": "routine",
        "raw_text": text[:500],
    }
