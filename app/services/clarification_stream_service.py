"""澄清流式分支编排（阶段 F）。

【职责】
    在 chat_stream_runner 调用 Provider 前，处理澄清发起/回答/跳过。
    brief 已含答案的维度不再追问；brief 足够完整时自动完成澄清并出大纲。
"""

import json
from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.clarification_constants import (
    CLARIFICATION_STATUS_COLLECTING,
    CLARIFICATION_STATUS_SKIPPED,
)
from app.core.creative_config_reader import load_clarification_config
from app.creative.clarification_brief_extractor import extract_brief_signals
from app.creative.clarification_intent_detector import should_start_clarification
from app.creative.clarification_question_filter import filter_questions_by_brief
from app.creative.clarification_templates import build_template_questions
from app.models.postgres.clarification_session_model import ClarificationSessionModel
from app.models.postgres.time_helper import utc_now
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.schemas.clarification import ClarificationAnswerItem
from app.services.clarification_finalize_service import finalize_clarification_session
from app.services.clarification_sse_frame_builder import (
    build_clarification_complete_frame,
    build_clarification_request_frame,
    build_requirements_summary_frame,
)
from app.services.clarification_summary_builder import format_clarification_user_message
from app.services.creative_plan_outline_trigger import try_build_outline_proposed_frame
from app.storage.postgres.clarification_questions_codec import encode_questions_json, parse_questions_bundle
from app.services.conversation_creation_type_writer import bind_conversation_creation_type
from app.storage.postgres.clarification_session_repository import ClarificationSessionRepository


@dataclass(frozen=True)
class ClarificationStreamOutcome:
    """澄清分支 SSE 输出。"""

    frames: tuple[str, ...]
    state: AgentState


def try_clarification_stream(
    request: ChatRequest,
    state: AgentState,
    db_session: Session | None,
) -> ClarificationStreamOutcome | None:
    """尝试走澄清分支；不适用时返回 None。"""
    cfg = load_clarification_config()
    if db_session is None:
        return None
    repo = ClarificationSessionRepository(db_session)
    if request.clarification_response is not None:
        return _handle_response(request, state, repo, db_session)
    if request.clarification_skip and cfg.allow_skip:
        return _handle_skip(request, state, repo)
    if not should_start_clarification(request, cfg):
        return None
    if _has_finished_session(repo, state.conversation_id):
        return None
    return _handle_start_or_auto(request, state, repo, db_session)


def _handle_start_or_auto(
    request: ChatRequest,
    state: AgentState,
    repo: ClarificationSessionRepository,
    db_session: Session,
) -> ClarificationStreamOutcome:
    """brief 已完整则自动完成，否则只展示未覆盖的偏好题。"""
    creation_type = request.creation_type or "novel"
    initial_brief = request.message.strip()
    all_questions = build_template_questions(creation_type)
    signals = extract_brief_signals(initial_brief)
    shown = filter_questions_by_brief(all_questions, signals)
    if not shown:
        return _auto_complete_from_brief(request, state, repo, db_session, all_questions, initial_brief)
    return _handle_start(state, repo, db_session, creation_type, initial_brief, shown, all_questions)


def _handle_start(
    state: AgentState,
    repo: ClarificationSessionRepository,
    db_session: Session,
    creation_type: str,
    initial_brief: str,
    shown_questions: list,
    all_questions: list,
) -> ClarificationStreamOutcome:
    """发起精简后的澄清问卷。"""
    session_id = str(uuid4())
    model = ClarificationSessionModel(
        session_id=session_id,
        conversation_id=state.conversation_id,
        project_id=state.project_id,
        creation_type=creation_type,
        status=CLARIFICATION_STATUS_COLLECTING,
        round=1,
        questions_json=encode_questions_json(initial_brief, shown_questions, all_questions),
        answers_json="[]",
        requirements_summary="",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    repo.insert(model)
    bind_conversation_creation_type(
        db_session,
        state.conversation_id,
        state.project_id,
        creation_type,
    )
    frame = build_clarification_request_frame(session_id, 1, shown_questions)
    answer = "已根据你的描述生成偏好问卷，仅需补充尚未说明的项。"
    return ClarificationStreamOutcome(frames=(frame,), state=state.model_copy(update={"answer": answer}))


def _auto_complete_from_brief(
    request: ChatRequest,
    state: AgentState,
    repo: ClarificationSessionRepository,
    db_session: Session,
    all_questions: list,
    initial_brief: str,
) -> ClarificationStreamOutcome:
    """brief 已覆盖全部维度：跳过问卷，直接摘要 + 大纲。"""
    session_id = str(uuid4())
    row = ClarificationSessionModel(
        session_id=session_id,
        conversation_id=state.conversation_id,
        project_id=state.project_id,
        creation_type=request.creation_type or "novel",
        status=CLARIFICATION_STATUS_COLLECTING,
        round=1,
        questions_json=encode_questions_json(initial_brief, [], all_questions),
        answers_json="[]",
        requirements_summary="",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    repo.insert(row)
    bind_conversation_creation_type(
        db_session,
        state.conversation_id,
        state.project_id,
        request.creation_type,
    )
    return _complete_and_build_frames(state, db_session, row, initial_brief, all_questions, [])


def _handle_response(
    request: ChatRequest,
    state: AgentState,
    repo: ClarificationSessionRepository,
    db_session: Session,
) -> ClarificationStreamOutcome | None:
    """处理用户提交的澄清答案。"""
    payload = request.clarification_response
    if payload is None:
        return None
    row = repo.get(payload.session_id)
    if row is None or row.status != CLARIFICATION_STATUS_COLLECTING:
        return None
    initial_brief, _shown, all_questions = parse_questions_bundle(row.questions_json)
    user_answers = [ClarificationAnswerItem.model_validate(a) for a in payload.answers]
    return _complete_and_build_frames(state, db_session, row, initial_brief, all_questions, user_answers)


def _complete_and_build_frames(
    state: AgentState,
    db_session: Session,
    row: ClarificationSessionModel,
    initial_brief: str,
    all_questions: list,
    user_answers: list[ClarificationAnswerItem],
) -> ClarificationStreamOutcome:
    """完成澄清并组装 SSE 帧（含可选 outline_proposed）。"""
    summary, answer_dicts = finalize_clarification_session(
        db_session, row, initial_brief, all_questions, user_answers,
    )
    frames_list = [
        build_requirements_summary_frame(row.session_id, summary, answer_dicts),
        build_clarification_complete_frame(row.session_id),
    ]
    outline_frame = try_build_outline_proposed_frame(
        db_session, state.conversation_id, state.project_id, row.creation_type, row.session_id,
    )
    if outline_frame is not None:
        frames_list.append(outline_frame)
    user_text = format_clarification_user_message(user_answers) if user_answers else initial_brief
    return ClarificationStreamOutcome(
        frames=tuple(frames_list),
        state=state.model_copy(update={"question": user_text, "answer": summary}),
    )


def _handle_skip(
    request: ChatRequest,
    state: AgentState,
    repo: ClarificationSessionRepository,
) -> ClarificationStreamOutcome | None:
    """记录跳过澄清。"""
    if not should_start_clarification(
        request.model_copy(update={"clarification_skip": False}),
        load_clarification_config(),
    ):
        return None
    session_id = str(uuid4())
    model = ClarificationSessionModel(
        session_id=session_id,
        conversation_id=state.conversation_id,
        project_id=state.project_id,
        creation_type=request.creation_type or "novel",
        status=CLARIFICATION_STATUS_SKIPPED,
        round=0,
        questions_json="[]",
        answers_json="[]",
        requirements_summary="",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    repo.insert(model)
    return None


def _has_finished_session(repo: ClarificationSessionRepository, conversation_id: str) -> bool:
    """会话是否已有完成或跳过的澄清。"""
    if repo.get_collecting_by_conversation(conversation_id) is not None:
        return True
    return repo.has_finished_for_conversation(conversation_id)
