"""Skill 列表 API 路由。

【职责】
    GET /skills：返回已注册 Skill 元数据，供前端下拉选择器使用。
"""

from fastapi import APIRouter

from app.api.api_constants import SKILLS_ROUTE_PREFIX
from app.schemas.skill_list import SkillListResponse
from app.services.skill_list_service import build_skill_list_response

router = APIRouter(prefix=SKILLS_ROUTE_PREFIX, tags=["skills"])


@router.get("", summary="Skill 列表")
def list_skills() -> SkillListResponse:
    """扫描 skills/ 目录并返回全部 Skill 元数据。

    返回:
        SkillListResponse: 不含 system_prompt 全文，避免响应过大。
    """
    return build_skill_list_response()
