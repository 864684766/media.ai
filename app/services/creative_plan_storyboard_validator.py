"""策划→分镜前置校验。"""

from app.core.creative_plan_constants import PLAN_STATUS_APPROVED
from app.core.plan_storyboard_constants import PLAN_STORYBOARD_CREATION_TYPE
from app.models.postgres.creative_plan_model import CreativePlanModel
from app.services.creative_plan_storyboard_errors import (
    CreativePlanStoryboardStatusError,
    CreativePlanStoryboardTypeError,
)


def validate_plan_for_storyboard(row: CreativePlanModel) -> None:
    """确认大纲状态与创作类型满足分镜生成条件。

    参数:
        row: 已加载的大纲 ORM。

    异常:
        CreativePlanStoryboardStatusError: 未 approved。
        CreativePlanStoryboardTypeError: 非 video 类型。
    """
    if row.status != PLAN_STATUS_APPROVED:
        raise CreativePlanStoryboardStatusError(f"当前状态 {row.status} 不可生成分镜")
    if row.creation_type != PLAN_STORYBOARD_CREATION_TYPE:
        raise CreativePlanStoryboardTypeError("仅视频大纲支持一键生成分镜")
