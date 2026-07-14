"""大纲 SSE 帧构造。"""

from app.core import constants
from app.schemas.creative_plan import CreativePlanItem
from app.services.chat_stream_formatter import format_sse_event


def build_outline_proposed_frame(plan: CreativePlanItem) -> str:
    """构造 outline_proposed 事件帧。"""
    payload = {
        constants.SSE_FIELD_PLAN_ID: plan.plan_id,
        constants.SSE_FIELD_PLAN_VERSION: plan.version,
        constants.SSE_FIELD_PLAN_TITLE: plan.title,
        constants.SSE_FIELD_PLAN_CONTENT_MD: plan.content_md,
        constants.SSE_FIELD_PLAN_CREATION_TYPE: plan.creation_type,
    }
    return format_sse_event(payload, constants.SSE_EVENT_OUTLINE_PROPOSED)


def build_outline_revised_frame(plan: CreativePlanItem) -> str:
    """构造 outline_revised 事件帧。"""
    payload = {
        constants.SSE_FIELD_PLAN_ID: plan.plan_id,
        constants.SSE_FIELD_PLAN_VERSION: plan.version,
        constants.SSE_FIELD_PLAN_CONTENT_MD: plan.content_md,
    }
    return format_sse_event(payload, constants.SSE_EVENT_OUTLINE_REVISED)


def build_outline_approved_frame(plan: CreativePlanItem) -> str:
    """构造 outline_approved 事件帧。"""
    approved_at = plan.approved_at.isoformat() if plan.approved_at else ""
    payload = {
        constants.SSE_FIELD_PLAN_ID: plan.plan_id,
        constants.SSE_FIELD_PLAN_APPROVED_AT: approved_at,
    }
    return format_sse_event(payload, constants.SSE_EVENT_OUTLINE_APPROVED)
