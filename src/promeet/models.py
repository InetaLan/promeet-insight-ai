from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date


class Priority(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    needs_review = "needs_review"
    validation_failed = "validation_failed"


class TranscriptSegment(BaseModel):
    segment_id: str
    timestamp: str
    speaker: str
    text: str
    status: str = "valid"


class ExtractedTask(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    task_name: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    assignee: str = Field(..., min_length=2)
    deadline: str = Field(..., description="YYYY-MM-DD arba 'deadline_missing'")
    priority: Priority = Priority.Medium
    source_quote: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_segment_id: str = Field(..., min_length=1)
    approval_status: ApprovalStatus = ApprovalStatus.pending
    validation_errors: list[str] = Field(default_factory=list)

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: str) -> str:
        if v == "deadline_missing":
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError("deadline must be YYYY-MM-DD or deadline_missing") from exc
        return v


class ExtractedDecision(BaseModel):
    decision: str
    source_quote: str | None = None
    source_segment_id: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    transcript_name: str
    tasks: list[ExtractedTask] = Field(default_factory=list)
    decisions: list[ExtractedDecision] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    open_questions: list[dict] = Field(default_factory=list)
    validation_summary: dict = Field(default_factory=dict)
