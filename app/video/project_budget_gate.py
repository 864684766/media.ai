"""项目预算熔断门控（V7）。

【职责】
    在 render/compose 启动前校验累计 cost + 预估是否超限。

【何时调用】
    render_job_service / compose_job_service 入口。
"""

from sqlalchemy.orm import Session

from app.video.project_budget_limit_resolver import resolve_project_budget_limit_usd
from app.video.project_cost_aggregator import sum_project_cost_usd
from app.video.video_budget_config_reader import VideoBudgetConfig


class BudgetExceededError(Exception):
    """预算超限，阻断 Job。"""

    def __init__(self, project_id: str, total: float, limit: float) -> None:
        """保存超限上下文。"""
        self.project_id = project_id
        self.total_cost_usd = total
        self.budget_limit_usd = limit
        super().__init__(f"budget exceeded: {total} > {limit}")


def assert_budget_allows(
    session: Session,
    project_id: str,
    budget: VideoBudgetConfig,
    estimated_addition: float,
) -> None:
    """校验预算；超限抛 BudgetExceededError。

    参数:
        session: DB Session。
        project_id: 项目 id。
        budget: 预算配置。
        estimated_addition: 本次 Job 预估增量成本。
    """
    limit = resolve_project_budget_limit_usd(session, project_id)
    if limit <= 0:
        return
    current = sum_project_cost_usd(session, project_id)
    projected = round(current + estimated_addition, 6)
    if projected > limit:
        raise BudgetExceededError(project_id, projected, limit)
