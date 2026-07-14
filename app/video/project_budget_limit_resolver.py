"""项目预算上限解析（V7/V8）。

【职责】
    优先 video_projects.budget_limit_usd，否则回退 app.yaml 全局默认。

【何时调用】
    project_budget_gate、GET cost API。
"""

from sqlalchemy.orm import Session

from app.storage.postgres.video_project_repository import VideoProjectRepository
from app.video.video_budget_config_reader import load_video_budget_config


def resolve_project_budget_limit_usd(session: Session, project_id: str) -> float:
    """解析单项目预算上限。

    参数:
        session: DB Session。
        project_id: 项目 id。

    返回:
        float: 0 表示不限额。
    """
    row = VideoProjectRepository(session).get(project_id)
    if row is not None and row.budget_limit_usd > 0:
        return row.budget_limit_usd
    return load_video_budget_config().default_limit_usd
