from promeet.schema import validate_task_dict


def test_valid_task_schema():
    task = {
        "task_name": "Paruošti modelių matricą",
        "description": "Parengti MVP modelių palyginimo matricą.",
        "assignee": "Agnė Urbonaitė",
        "deadline": "2026-05-22",
        "priority": "High",
        "source_quote": "Agnė, paruošk modelių matricą iki penktadienio",
        "confidence_score": 0.91,
        "source_segment_id": "SEG-0001",
    }
    parsed, errors = validate_task_dict(task)
    assert parsed is not None
    assert errors == []


def test_invalid_missing_required_field():
    task = {
        "task_name": "Paruošti modelių matricą",
        "description": "Parengti MVP modelių palyginimo matricą.",
        "deadline": "2026-05-22",
        "priority": "High",
        "source_quote": None,
        "confidence_score": 0.91,
        "source_segment_id": "SEG-0001",
    }
    parsed, errors = validate_task_dict(task)
    assert parsed is None
    assert any("assignee" in e for e in errors)


def test_invalid_deadline_format():
    task = {
        "task_name": "Paruošti modelių matricą",
        "description": "Parengti MVP modelių palyginimo matricą.",
        "assignee": "Agnė Urbonaitė",
        "deadline": "next Friday",
        "priority": "High",
        "source_quote": None,
        "confidence_score": 0.91,
        "source_segment_id": "SEG-0001",
    }
    parsed, errors = validate_task_dict(task)
    assert parsed is None
    assert any("deadline" in e for e in errors)
