"""创作大纲 REST API。"""

from fastapi import APIRouter, HTTPException, Query

from app.api.api_constants import CREATIVE_ROUTE_PREFIX
from app.schemas.creative_plan import (
    CreativePlanCreateRequest,
    CreativePlanDetailResponse,
    CreativePlanListResponse,
    CreativePlanPatchRequest,
    CreativePlanReviseRequest,
    CreativePlanStoryboardRequest,
    CreativePlanStoryboardResponse,
)
from app.services.creative_plan_approve_service import approve_creative_plan
from app.services.creative_plan_create_service import create_creative_plan
from app.services.creative_plan_errors import (
    ClarificationRequiredError,
    CreativePlanNotFoundError,
    CreativePlanRevisionLimitError,
    CreativePlanStatusError,
)
from app.services.creative_plan_patch_service import patch_creative_plan
from app.services.creative_plan_query_service import (
    get_creative_plan,
    list_creative_plans_by_conversation,
)
from app.services.creative_plan_revise_service import revise_creative_plan
from app.services.creative_plan_storyboard_errors import (
    CreativePlanStoryboardNotFoundError,
    CreativePlanStoryboardProjectError,
    CreativePlanStoryboardStatusError,
    CreativePlanStoryboardTypeError,
)
from app.services.creative_plan_storyboard_service import generate_storyboard_from_approved_plan
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=CREATIVE_ROUTE_PREFIX, tags=["creative"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.post("/plans", summary="生成创作大纲 v1", response_model=CreativePlanDetailResponse)
def post_create_plan(body: CreativePlanCreateRequest) -> CreativePlanDetailResponse:
    """根据澄清摘要或 brief 创建大纲。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            plan = create_creative_plan(session, body)
            return CreativePlanDetailResponse(plan=plan)
    except ClarificationRequiredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/plans/{plan_id}", summary="查询大纲", response_model=CreativePlanDetailResponse)
def get_plan_detail(plan_id: str) -> CreativePlanDetailResponse:
    """按 plan_id 返回大纲详情。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            plan = get_creative_plan(session, plan_id)
            return CreativePlanDetailResponse(plan=plan)
    except CreativePlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"大纲不存在: {exc}") from exc


@router.get("/plans", summary="会话下最新大纲", response_model=CreativePlanListResponse)
def get_plans_by_conversation(
    conversation_id: str = Query(..., description="会话 id"),
) -> CreativePlanListResponse:
    """按 conversation_id 查询最新大纲。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_creative_plans_by_conversation(session, conversation_id)


@router.patch("/plans/{plan_id}", summary="手工编辑大纲", response_model=CreativePlanDetailResponse)
def patch_plan(plan_id: str, body: CreativePlanPatchRequest) -> CreativePlanDetailResponse:
    """用户直接修改 content_md。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            plan = patch_creative_plan(session, plan_id, body)
            return CreativePlanDetailResponse(plan=plan)
    except CreativePlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"大纲不存在: {exc}") from exc
    except CreativePlanStatusError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/plans/{plan_id}/revise", summary="AI 改稿", response_model=CreativePlanDetailResponse)
def post_revise_plan(
    plan_id: str,
    body: CreativePlanReviseRequest,
) -> CreativePlanDetailResponse:
    """根据用户意见改稿。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            plan = revise_creative_plan(session, plan_id, body)
            return CreativePlanDetailResponse(plan=plan)
    except CreativePlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"大纲不存在: {exc}") from exc
    except (CreativePlanStatusError, CreativePlanRevisionLimitError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/plans/{plan_id}/approve", summary="确认大纲", response_model=CreativePlanDetailResponse)
def post_approve_plan(plan_id: str) -> CreativePlanDetailResponse:
    """锁定大纲为 approved。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            plan = approve_creative_plan(session, plan_id)
            return CreativePlanDetailResponse(plan=plan)
    except CreativePlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"大纲不存在: {exc}") from exc
    except CreativePlanStatusError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/plans/{plan_id}/storyboard",
    summary="按已确认大纲生成分镜",
    response_model=CreativePlanStoryboardResponse,
)
def post_plan_storyboard(
    plan_id: str,
    body: CreativePlanStoryboardRequest | None = None,
) -> CreativePlanStoryboardResponse:
    """将 approved 视频大纲拆为结构化分镜并入库。"""
    _require_postgres()
    payload = body or CreativePlanStoryboardRequest()
    try:
        with postgres_session_scope() as session:
            return generate_storyboard_from_approved_plan(session, plan_id, payload)
    except CreativePlanStoryboardNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"大纲不存在: {exc.plan_id}") from exc
    except CreativePlanStoryboardStatusError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except CreativePlanStoryboardTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CreativePlanStoryboardProjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
