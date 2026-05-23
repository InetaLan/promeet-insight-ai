from __future__ import annotations

from .models import ExtractedTask
from .config import settings


def to_jira_payload(task: ExtractedTask) -> dict:
    description_text = (
        f"{task.description}\n\n"
        f"AI confidence: {task.confidence_score}\n"
        f"Source segment: {task.source_segment_id}\n"
        f"Source quote for PM review: {task.source_quote or 'N/A'}"
    )

    fields = {
        "project": {"key": settings.jira_project_key},
        "summary": task.task_name,
        "issuetype": {"name": settings.jira_issue_type},
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": description_text}]}
            ],
        },
        "priority": {"name": task.priority},
    }

    if task.deadline != "deadline_missing":
        fields["duedate"] = task.deadline

    return {"fields": fields}


def mock_create_jira_issue(task: ExtractedTask, index: int) -> dict:
    return {
        "mock": True,
        "jira_key": f"{settings.jira_project_key}-{1000 + index}",
        "status": "created",
        "payload": to_jira_payload(task),
    }
