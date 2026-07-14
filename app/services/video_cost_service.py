"""视频项目成本查询服务（V7）。

【职责】
    聚合 shot_assets cost 并附带 budget / Provider 选型信息。

【何时调用】
    GET /video/projects/{id}/cost API。
"""

from sqlalchemy.orm import Session

from app.schemas.video_cost import ActiveProvidersOutput, ProjectCostOutput
from app.storage.postgres.shot_asset_repository import ShotAssetRepository
from app.video.project_cost_aggregator import sum_project_cost_usd
from app.video.project_budget_limit_resolver import resolve_project_budget_limit_usd
from app.video.video_provider_config_reader import load_video_provider_config


def get_project_cost(session: Session, project_id: str) -> ProjectCostOutput:
    """查询项目成本摘要。

    参数:
        session: DB Session。
        project_id: 项目 id。

    返回:
        ProjectCostOutput: 成本与预算状态。
    """
    total = sum_project_cost_usd(session, project_id)
    providers = load_video_provider_config()
    limit = resolve_project_budget_limit_usd(session, project_id)
    remaining = _remaining_usd(total, limit)
    assets = ShotAssetRepository(session).list_by_project(project_id)
    return ProjectCostOutput(
        project_id=project_id,
        total_cost_usd=total,
        budget_limit_usd=limit,
        remaining_usd=remaining,
        budget_exceeded=_is_exceeded(total, limit),
        asset_count=len(assets),
        active_providers=ActiveProvidersOutput(
            keyframe=providers.active_keyframe,
            clip=providers.active_clip,
            compose=providers.active_compose,
        ),
    )


def _remaining_usd(total: float, limit: float) -> float:
    """计算剩余预算。"""
    if limit <= 0:
        return 0.0
    return round(max(limit - total, 0.0), 6)


def _is_exceeded(total: float, limit: float) -> bool:
    """是否已超预算。"""
    if limit <= 0:
        return False
    return total > limit
