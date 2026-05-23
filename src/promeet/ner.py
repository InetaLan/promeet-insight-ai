from __future__ import annotations

import re
from .models import TranscriptSegment

PERSON_RE = re.compile(r"\b[A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž]+(?:\s+[A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž]+)?\b")


def simple_ner(segments: list[TranscriptSegment]) -> dict:
    persons = set()
    dates = set()
    for s in segments:
        persons.add(s.speaker)
        for p in PERSON_RE.findall(s.text):
            if len(p) > 2:
                persons.add(p)
        for d in re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", s.text):
            dates.add(d)
    return {"persons": sorted(persons), "dates": sorted(dates)}
