from __future__ import annotations

from .models import ExtractedTask


def field_completeness_score(task: ExtractedTask) -> float:
    fields = [
        bool(task.task_name.strip()),
        bool(task.description.strip()),
        bool(task.assignee.strip()),
        task.deadline != "deadline_missing",
        task.source_quote is not None and bool(task.source_quote.strip()),
    ]
    return sum(fields) / len(fields)


def hybrid_confidence(task: ExtractedTask, similarity_score: float = 0.0, ner_match: bool = True) -> float:
    llm_score = task.confidence_score
    completeness = field_completeness_score(task)
    ner_score = 1.0 if ner_match else 0.55
    score = 0.40 * llm_score + 0.20 * ner_score + 0.20 * similarity_score + 0.20 * completeness
    return round(max(0.0, min(1.0, score)), 3)


def apply_governance_status(task: ExtractedTask) -> ExtractedTask:
    if task.confidence_score < 0.70 or task.deadline == "deadline_missing":
        task.approval_status = "needs_review"
    else:
        task.approval_status = "pending"
    return task
