from __future__ import annotations

import re
from datetime import date, timedelta
from .models import TranscriptSegment

ACTION_PATTERNS = [
    r"\b(aš|as)\s+(pasiimu|paruošiu|padarysiu|aprašysiu|sukursiu|patikrinsiu|pridėsiu|paziuresiu|pažiūrėsiu)\b",
    r"\b([A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž]+),\s*(paruošk|sukurk|aprašyk|patikrink|pridėk)\b",
    r"\breikia\s+(parengti|sukurti|aprašyti|patikrinti|pridėti|validuoti)\b",
    r"\b(siūlau|sutarta|pažymiu kaip sprendimą)\b",
]

DATE_HINTS = {
    "iki penktadienio": 4,
    "iki kito penktadienio": 11,
    "iki kito trečiadienio": 9,
    "iki sprinto pabaigos": 14,
    "iki kito review": 7,
    "iki pilot readiness patikros": 14,
}


def resolve_relative_deadline(text: str, meeting_date: date | None = None) -> str:
    base = meeting_date or date.today()
    lower = text.lower()
    for phrase, days in DATE_HINTS.items():
        if phrase in lower:
            return (base + timedelta(days=days)).isoformat()
    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if m:
        return m.group(1)
    return "deadline_missing"


def infer_priority(text: str) -> str:
    lower = text.lower()
    if any(x in lower for x in ["kriti", "critical", "incident", "skubu", "aukštas", "high"]):
        return "High"
    if any(x in lower for x in ["rizika", "gdpr", "api klaida", "klaida"]):
        return "High"
    return "Medium"


def infer_assignee(segment: TranscriptSegment) -> str:
    m = re.match(r"([A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž]+)", segment.text.strip())
    if m and "," in segment.text[:30]:
        return m.group(1)
    if re.search(r"\b(aš|as)\s+(pasiimu|paruošiu|padarysiu|aprašysiu|sukursiu|patikrinsiu|pridėsiu|pažiūrėsiu|paziuresiu)\b", segment.text, re.I):
        return segment.speaker
    return segment.speaker


def make_task_name(text: str) -> str:
    cleaned = re.sub(r"^(Aš|As)\s+", "", text.strip(), flags=re.I)
    cleaned = re.sub(r"^(sutinku\.?\s*)", "", cleaned, flags=re.I)
    cleaned = cleaned[:90].strip(" .")
    return cleaned if len(cleaned) >= 3 else "Peržiūrėti meetingo veiksmą"


def extract_rule_based(segments: list[TranscriptSegment], meeting_date: date | None = None) -> dict:
    tasks = []
    decisions = []
    risks = []

    for s in segments:
        text = s.text.strip()
        lower = text.lower()
        is_action = any(re.search(p, lower, re.I) for p in ACTION_PATTERNS)
        is_risk = any(w in lower for w in ["rizika", "klaida", "gdpr", "jautri informacija", "konfidencial"])
        is_decision = any(w in lower for w in ["sprendimą", "sutarta", "pažymiu kaip sprendimą"])

        if is_action and not lower.startswith(("galėtume", "galime", "pažiūrėkim")):
            confidence = 0.68
            if "iki " in lower:
                confidence += 0.12
            if s.speaker:
                confidence += 0.08
            if is_decision:
                confidence += 0.04

            tasks.append({
                "task_name": make_task_name(text),
                "description": text,
                "assignee": infer_assignee(s),
                "deadline": resolve_relative_deadline(text, meeting_date),
                "priority": infer_priority(text),
                "source_quote": text,
                "confidence_score": min(confidence, 0.95),
                "source_segment_id": s.segment_id,
            })

        if is_decision:
            decisions.append({
                "decision": text,
                "source_quote": text,
                "source_segment_id": s.segment_id,
                "confidence_score": 0.78,
            })

        if is_risk:
            risks.append({
                "risk": text,
                "source_quote": text,
                "source_segment_id": s.segment_id,
                "confidence_score": 0.72,
            })

    return {"tasks": tasks, "decisions": decisions, "risks": risks, "open_questions": []}
