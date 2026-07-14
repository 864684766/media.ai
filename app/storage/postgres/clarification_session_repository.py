"""澄清会话 Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clarification_constants import (
    CLARIFICATION_STATUS_COLLECTING,
    CLARIFICATION_STATUS_COMPLETED,
    CLARIFICATION_STATUS_SKIPPED,
)
from app.models.postgres.clarification_session_model import ClarificationSessionModel


class ClarificationSessionRepository:
    """clarification_sessions 表访问。"""

    def __init__(self, session: Session) -> None:
        """绑定 SQLAlchemy Session。"""
        self._session = session

    def get(self, session_id: str) -> ClarificationSessionModel | None:
        """按主键查询。"""
        return self._session.get(ClarificationSessionModel, session_id)

    def get_collecting_by_conversation(
        self,
        conversation_id: str,
    ) -> ClarificationSessionModel | None:
        """查询会话下进行中的澄清。"""
        stmt = (
            select(ClarificationSessionModel)
            .where(ClarificationSessionModel.conversation_id == conversation_id)
            .where(ClarificationSessionModel.status == CLARIFICATION_STATUS_COLLECTING)
            .order_by(ClarificationSessionModel.updated_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def has_finished_for_conversation(self, conversation_id: str) -> bool:
        """会话是否已有 completed 或 skipped 记录。"""
        stmt = (
            select(ClarificationSessionModel.session_id)
            .where(ClarificationSessionModel.conversation_id == conversation_id)
            .where(
                ClarificationSessionModel.status.in_(
                    (CLARIFICATION_STATUS_COMPLETED, CLARIFICATION_STATUS_SKIPPED),
                ),
            )
            .limit(1)
        )
        return self._session.scalars(stmt).first() is not None

    def insert(self, model: ClarificationSessionModel) -> ClarificationSessionModel:
        """插入记录。"""
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model

    def save(self, model: ClarificationSessionModel) -> ClarificationSessionModel:
        """更新记录。"""
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model

    def get_latest_by_conversation(
        self,
        conversation_id: str,
    ) -> ClarificationSessionModel | None:
        """查询会话下最近一条澄清记录（任意状态）。"""
        stmt = (
            select(ClarificationSessionModel)
            .where(ClarificationSessionModel.conversation_id == conversation_id)
            .order_by(ClarificationSessionModel.updated_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def get_latest_completed_by_conversation(
        self,
        conversation_id: str,
    ) -> ClarificationSessionModel | None:
        """查询会话下最近完成的澄清（含 requirements_summary）。"""
        stmt = (
            select(ClarificationSessionModel)
            .where(ClarificationSessionModel.conversation_id == conversation_id)
            .where(ClarificationSessionModel.status == CLARIFICATION_STATUS_COMPLETED)
            .order_by(ClarificationSessionModel.updated_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()
