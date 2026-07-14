"""项目成本聚合（V7）。

【职责】
    从 shot_assets 汇总 project 已发生 cost。

【何时调用】
    GET cost API 与 budget 熔断前查询。
"""

from sqlalchemy.orm import Session

from app.storage.postgres.shot_asset_repository import ShotAssetRepository


def sum_project_cost_usd(session: Session, project_id: str) -> float:
    """汇总 project 下全部资产 cost。

    参数:
        session: SQLAlchemy Session。
        project_id: 项目 id。

    返回:
        float: 累计成本。
    """
    total = ShotAssetRepository(session).sum_cost_by_project(project_id)
    return round(float(total), 6)
