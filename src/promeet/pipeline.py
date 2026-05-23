from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from .docx_loader import read_transcript_file
from .parser import parse_segments, validate_transcript_structure
from .rule_based_extractor import extract_rule_based
from .llm_extractor import extract_with_openai
from .schema import validate_tasks
from .models import ExtractionResult, ExtractedDecision
from .ner import simple_ner
from .similarity import SimilarityEngine
from .confidence import hybrid_confidence, apply_governance_status
from .jira_mapper import mock_create_jira_issue


def process_transcript(path: str | Path, use_openai: bool = False, meeting_date: date | None = None) -> ExtractionResult:
    path = Path(path)
    raw_text = read_transcript_file(path)
    segments = parse_segments(raw_text)
    validation = validate_transcript_structure(segments)
    ner_result = simple_ner(segments)

    if validation["status"] == "rejected":
        return ExtractionResult(transcript_name=path.name, validation_summary=validation)

    if use_openai:
        try:
            extracted = extract_with_openai(segments)
            extraction_mode = "openai_gpt4o"
        except Exception as exc:
            extracted = extract_rule_based(segments, meeting_date=meeting_date)
            extraction_mode = f"rule_based_fallback_after_openai_error: {exc}"
    else:
        extracted = extract_rule_based(segments, meeting_date=meeting_date)
        extraction_mode = "rule_based_demo"

    valid_tasks, invalid_tasks = validate_tasks(extracted.get("tasks", []))
    sim = SimilarityEngine()
    source_texts = [s.text for s in segments]

    enriched_tasks = []
    for task in valid_tasks:
        similarity = sim.max_similarity(task.source_quote or task.description, source_texts)
        ner_match = task.assignee in ner_result["persons"] or any(task.assignee in p for p in ner_result["persons"])
        task.confidence_score = hybrid_confidence(task, similarity_score=similarity, ner_match=ner_match)
        enriched_tasks.append(apply_governance_status(task))

    decisions = []
    for d in extracted.get("decisions", []):
        try:
            decisions.append(ExtractedDecision.model_validate(d))
        except Exception:
            pass

    summary = {
        **validation,
        "extraction_mode": extraction_mode,
        "ner": ner_result,
        "invalid_task_count": len(invalid_tasks),
        "invalid_tasks": invalid_tasks,
    }

    return ExtractionResult(
        transcript_name=path.name,
        tasks=enriched_tasks,
        decisions=decisions,
        risks=extracted.get("risks", []),
        open_questions=extracted.get("open_questions", []),
        validation_summary=summary,
    )


def save_result(result: ExtractionResult, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{Path(result.transcript_name).stem}_result.json"
    out_path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def save_jira_payloads(result: ExtractionResult, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = [mock_create_jira_issue(task, idx + 1) for idx, task in enumerate(result.tasks)]
    out_path = output_dir / f"{Path(result.transcript_name).stem}_jira_payloads.json"
    out_path.write_text(json.dumps(payloads, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
