"""创作大纲 Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.creative_plan_constants import PLAN_STATUS_APPROVED
from app.models.postgres.creative_plan_model import CreativePlanModel


class CreativePlanRepository:
    """creative_plans 表访问。"""

    def __init__(self, session: Session) -> None:
        """绑定 SQLAlchemy Session。"""
        self._session = session

    def get(self, plan_id: str) -> CreativePlanModel | None:
        """按主键查询。"""
        return self._session.get(CreativePlanModel, plan_id)

    def get_latest_by_conversation(self, conversation_id: str) -> CreativePlanModel | None:
        """查询会话下最新大纲。"""
        stmt = (
            select(CreativePlanModel)
            .where(CreativePlanModel.conversation_id == conversation_id)
            .order_by(CreativePlanModel.updated_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def has_approved_for_conversation(self, conversation_id: str) -> bool:
        """会话是否已有 approved 大纲。"""
        stmt = (
            select(CreativePlanModel.plan_id)
            .where(CreativePlanModel.conversation_id == conversation_id)
            .where(CreativePlanModel.status == PLAN_STATUS_APPROVED)
            .limit(1)
        )
        return self._session.scalars(stmt).first() is not None

    def get_approved_by_conversation(self, conversation_id: str) -> CreativePlanModel | None:
        """查询会话下已 approved 的大纲（最新一条）。"""
        stmt = (
            select(CreativePlanModel)
            .where(CreativePlanModel.conversation_id == conversation_id)
            .where(CreativePlanModel.status == PLAN_STATUS_APPROVED)
            .order_by(CreativePlanModel.approved_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def insert(self, model: CreativePlanModel) -> CreativePlanModel:
        """插入记录。"""
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model

    def save(self, model: CreativePlanModel) -> CreativePlanModel:
        """更新记录。"""
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model
