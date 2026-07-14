"""澄清会话完成：合并 brief 预填与用户答案并写摘要。"""

import json

from sqlalchemy.orm import Session

from app.creative.clarification_brief_extractor import extract_brief_signals
from app.creative.clarification_question_filter import (
    build_prefilled_answers,
    merge_answer_lists,
)
from app.models.postgres.clarification_session_model import ClarificationSessionModel
from app.models.postgres.time_helper import utc_now
from app.schemas.clarification import ClarificationAnswerItem, ClarificationQuestionItem
from app.core.clarification_constants import CLARIFICATION_STATUS_COMPLETED
from app.services.clarification_summary_builder import build_requirements_summary
from app.storage.postgres.clarification_session_repository import ClarificationSessionRepository


def finalize_clarification_session(
    session: Session,
    row: ClarificationSessionModel,
    initial_brief: str,
    all_questions: list[ClarificationQuestionItem],
    user_answers: list[ClarificationAnswerItem],
) -> tuple[str, list[dict]]:
    """合并答案、写 requirements_summary 并标记 completed。"""
    prefilled = build_prefilled_answers(all_questions, extract_brief_signals(initial_brief))
    merged = merge_answer_lists(prefilled, user_answers)
    answer_dicts = [item.model_dump() for item in merged]
    summary = build_requirements_summary(row.creation_type, all_questions, answer_dicts, initial_brief)
    row.answers_json = json.dumps(answer_dicts, ensure_ascii=False)
    row.requirements_summary = summary
    row.status = CLARIFICATION_STATUS_COMPLETED
    row.updated_at = utc_now()
    ClarificationSessionRepository(session).save(row)
    return summary, answer_dicts
