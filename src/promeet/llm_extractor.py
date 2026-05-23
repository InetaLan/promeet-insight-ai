from __future__ import annotations

import json
from openai import OpenAI
from .config import settings
from .parser import transcript_for_llm
from .models import TranscriptSegment

TASK_SCHEMA = {
    "name": "promeet_extraction_result",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task_name": {"type": "string"},
                        "description": {"type": "string"},
                        "assignee": {"type": "string"},
                        "deadline": {"type": "string", "description": "YYYY-MM-DD or deadline_missing"},
                        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                        "source_quote": {"type": ["string", "null"]},
                        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "source_segment_id": {"type": "string"}
                    },
                    "required": [
                        "task_name",
                        "description",
                        "assignee",
                        "deadline",
                        "priority",
                        "source_quote",
                        "confidence_score",
                        "source_segment_id"
                    ]
                }
            },
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "decision": {"type": "string"},
                        "source_quote": {"type": ["string", "null"]},
                        "source_segment_id": {"type": "string"},
                        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["decision", "source_quote", "source_segment_id", "confidence_score"]
                }
            },
            "risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "risk": {"type": "string"},
                        "source_quote": {"type": ["string", "null"]},
                        "source_segment_id": {"type": "string"},
                        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["risk", "source_quote", "source_segment_id", "confidence_score"]
                }
},
            "open_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question": {"type": "string"},
                        "source_quote": {"type": ["string", "null"]},
                        "source_segment_id": {"type": "string"},
                        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["question", "source_quote", "source_segment_id", "confidence_score"]
                }
            }
        },
        "required": ["tasks", "decisions", "risks", "open_questions"]
    },
    "strict": True
}

SYSTEM_PROMPT = """
You are ProMeet Insight AI. Extract project-management artifacts from a validated MS Teams transcript.

Return JSON only according to the provided schema.

Rules:
- Extract only real commitments, not vague discussions.
- If the speaker says "aš paruošiu", assignee is that speaker.
- If deadline is unclear, use "deadline_missing".
- Use source_segment_id exactly as provided.
- source_quote must be a direct quote or short excerpt from the transcript.
- priority must be Low, Medium, High, or Critical.
- Sensitive information must not be copied into description unless needed; keep source_quote for PM review.
- If confidence is low, still return the task but lower confidence_score.
"""


def extract_with_openai(segments: list[TranscriptSegment]) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=settings.openai_api_key)
    transcript = transcript_for_llm(segments)

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": TASK_SCHEMA,
        },
    )

    content = response.choices[0].message.content
    return json.loads(content)
