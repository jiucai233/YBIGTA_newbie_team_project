import json
from pathlib import Path
from typing import Any

from st_app.utils.state import GraphState


SUBJECTS_PATH = Path(__file__).resolve().parents[2] / "db" / "subjects.json"


def _load_subjects() -> list[dict[str, Any]]:
    if not SUBJECTS_PATH.exists():
        return []

    try:
        with SUBJECTS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    subjects = data.get("subjects", [])
    if isinstance(subjects, list):
        return [item for item in subjects if isinstance(item, dict)]
    return []


def _score_subject(user_input: str, subject: dict[str, Any]) -> int:
    score = 0
    for kw in subject.get("keywords", []):
        if isinstance(kw, str) and kw and kw.lower() in user_input:
            score += 1
    return score


def subject_info_node(state: GraphState) -> dict:
    """
    Subject 정보 노드.
    사용자 질문과 subjects.json의 키워드를 매칭하여 관련 정보를 반환한다.
    """
    print("---SUBJECT INFO NODE---")

    user_input = state.get("user_input", "").strip().lower()
    subjects = _load_subjects()

    if not subjects:
        msg = "subject 정보 데이터가 비어 있습니다. st_app/db/subjects.json을 채워주세요."
        return {"subject": msg, "context": msg}

    scored = []
    for subject in subjects:
        score = _score_subject(user_input, subject)
        if score > 0:
            scored.append((score, subject))

    if not scored:
        available_topics = ", ".join(s.get("title", "") for s in subjects[:6] if s.get("title"))
        msg = (
            "요청하신 주제를 정확히 찾지 못했어요. "
            f"다음 주제로 물어보면 더 정확히 답할 수 있어요: {available_topics}"
        )
        return {"subject": msg, "context": msg}

    scored.sort(key=lambda x: x[0], reverse=True)
    top_subjects = [item[1] for item in scored[:3]]

    sections: list[str] = []
    for item in top_subjects:
        title = item.get("title", "주제 정보")
        summary = item.get("summary", "")
        details = item.get("details", [])

        lines = [f"[{title}]", summary]
        if isinstance(details, list):
            for detail in details[:3]:
                if isinstance(detail, str) and detail.strip():
                    lines.append(f"- {detail}")
        sections.append("\n".join(lines).strip())

    subject_context = "\n\n".join(sections)
    return {"subject": subject_context, "context": subject_context}
