"""澄清 SSE 帧构造。"""

from app.core import constants
from app.schemas.clarification import ClarificationQuestionItem
from app.storage.postgres.clarification_questions_codec import parse_questions_bundle
from app.services.chat_stream_formatter import format_sse_event


def build_clarification_request_frame(
    session_id: str,
    round_no: int,
    questions: list[ClarificationQuestionItem],
) -> str:
    """构造 clarification_request 事件帧。"""
    payload = {
        constants.SSE_FIELD_CLARIFICATION_SESSION_ID: session_id,
        constants.SSE_FIELD_CLARIFICATION_ROUND: round_no,
        constants.SSE_FIELD_CLARIFICATION_QUESTIONS: [q.model_dump() for q in questions],
    }
    return format_sse_event(payload, constants.SSE_EVENT_CLARIFICATION_REQUEST)


def build_requirements_summary_frame(session_id: str, summary_md: str, answers: list[dict]) -> str:
    """构造 requirements_summary 事件帧。"""
    payload = {
        constants.SSE_FIELD_CLARIFICATION_SESSION_ID: session_id,
        constants.SSE_FIELD_REQUIREMENTS_SUMMARY: summary_md,
        constants.SSE_FIELD_ANSWERS_SNAPSHOT: answers,
    }
    return format_sse_event(payload, constants.SSE_EVENT_REQUIREMENTS_SUMMARY)


def build_clarification_complete_frame(session_id: str) -> str:
    """构造 clarification_complete 事件帧。"""
    payload = {constants.SSE_FIELD_CLARIFICATION_SESSION_ID: session_id}
    return format_sse_event(payload, constants.SSE_EVENT_CLARIFICATION_COMPLETE)


def parse_questions_json(raw: str) -> list:
    """从 questions_json 反序列化展示用题目（兼容旧格式）。"""
    _brief, shown, _all = parse_questions_bundle(raw)
    return shown
