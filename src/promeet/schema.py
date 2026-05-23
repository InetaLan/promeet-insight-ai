from __future__ import annotations

from pydantic import ValidationError
from .models import ExtractedTask


def validate_task_dict(task: dict) -> tuple[ExtractedTask | None, list[str]]:
    try:
        parsed = ExtractedTask.model_validate(task)
        return parsed, []
    except ValidationError as exc:
        errors = []
        for e in exc.errors():
            loc = ".".join(str(x) for x in e.get("loc", []))
            msg = e.get("msg", "invalid")
            errors.append(f"{loc}: {msg}")
        return None, errors


def validate_tasks(tasks: list[dict]) -> tuple[list[ExtractedTask], list[dict]]:
    valid: list[ExtractedTask] = []
    invalid: list[dict] = []
    for task in tasks:
        parsed, errors = validate_task_dict(task)
        if parsed:
            valid.append(parsed)
        else:
            invalid.append({"raw_task": task, "errors": errors})
    return valid, invalid
