"""clarification_sessions.questions_json 编解码。"""

import json

from app.core.clarification_brief_constants import (
    QUESTIONS_JSON_KEY_BRIEF,
    QUESTIONS_JSON_KEY_ITEMS,
)
from app.schemas.clarification import ClarificationQuestionItem

QUESTIONS_JSON_KEY_ALL = "all_questions"


def encode_questions_json(
    initial_brief: str,
    shown_questions: list[ClarificationQuestionItem],
    all_questions: list[ClarificationQuestionItem],
) -> str:
    """写入带 initial_brief 与全量题目的 questions_json。"""
    payload = {
        QUESTIONS_JSON_KEY_BRIEF: initial_brief,
        QUESTIONS_JSON_KEY_ITEMS: [q.model_dump() for q in shown_questions],
        QUESTIONS_JSON_KEY_ALL: [q.model_dump() for q in all_questions],
    }
    return json.dumps(payload, ensure_ascii=False)


def parse_questions_bundle(raw: str) -> tuple[str, list[ClarificationQuestionItem], list[ClarificationQuestionItem]]:
    """解析 questions_json，返回 (initial_brief, shown, all)。"""
    if not raw.strip():
        return "", [], []
    data = json.loads(raw)
    if isinstance(data, list):
        items = _validate_questions(data)
        return "", items, items
    if not isinstance(data, dict):
        return "", [], []
    brief = str(data.get(QUESTIONS_JSON_KEY_BRIEF, "") or "")
    shown = _read_question_list(data.get(QUESTIONS_JSON_KEY_ITEMS))
    all_items = _read_question_list(data.get(QUESTIONS_JSON_KEY_ALL)) or shown
    return brief, shown, all_items


def _read_question_list(raw_items: object) -> list[ClarificationQuestionItem]:
    """读取题目列表字段。"""
    if not isinstance(raw_items, list):
        return []
    return _validate_questions(raw_items)


def _validate_questions(items: list) -> list[ClarificationQuestionItem]:
    """校验题目列表。"""
    return [ClarificationQuestionItem.model_validate(item) for item in items]
