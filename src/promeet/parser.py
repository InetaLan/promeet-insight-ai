from __future__ import annotations

import re
from .models import TranscriptSegment

SEGMENT_RE = re.compile(
    r"\[(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?P<speaker>[^:\n]{2,80}):\s*(?P<text>.*?)(?=\n\[\d{1,2}:\d{2}(?::\d{2})?\]\s*[^:\n]{2,80}:|\Z)",
    flags=re.DOTALL,
)


def parse_segments(raw_text: str) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    for idx, match in enumerate(SEGMENT_RE.finditer(raw_text), start=1):
        text = " ".join(match.group("text").split())
        segments.append(
            TranscriptSegment(
                segment_id=f"SEG-{idx:04d}",
                timestamp=match.group("timestamp"),
                speaker=" ".join(match.group("speaker").split()),
                text=text,
            )
        )
    return segments


def validate_transcript_structure(segments: list[TranscriptSegment]) -> dict:
    errors = []
    warnings = []

    if not segments:
        errors.append("No transcript segments detected. Expected format: [00:11] Speaker: text")

    for s in segments:
        if not s.speaker.strip():
            errors.append(f"{s.segment_id}: missing speaker")
        if not s.text.strip():
            errors.append(f"{s.segment_id}: missing text")
        if len(s.text.split()) < 3:
            warnings.append(f"{s.segment_id}: very short segment")

    status = "valid"
    if errors:
        status = "rejected"
    elif warnings:
        status = "warning"

    return {
        "status": status,
        "segment_count": len(segments),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def transcript_for_llm(segments: list[TranscriptSegment], max_chars: int = 45000) -> str:
    lines = [f"{s.segment_id} [{s.timestamp}] {s.speaker}: {s.text}" for s in segments]
    return "\n".join(lines)[:max_chars]
