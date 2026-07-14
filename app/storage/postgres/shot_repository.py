"""PostgreSQL 分镜 Repository。

【职责】
    封装 shots 表读写：按 project 列表、全量替换提交、删除旧镜头。

【为何独立 Repository】
    video API / CLI 不直接写 SQLAlchemy 查询，通过本类表达「提交分镜」「列出分镜」。
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.video_constants import (
    SHOT_STATUS_AWAITING_REVIEW,
    SHOT_STATUS_COMPOSED,
    SHOT_STATUS_DRAFT,
    SHOT_STATUS_QA_FAILED,
    SHOT_STATUS_QA_PASSED,
    SHOT_STATUS_REJECTED,
    SHOT_STATUS_RENDERED,
    SHOT_STATUS_VALIDATED,
)
from app.models.postgres.shot_model import ShotModel
from app.models.postgres.time_helper import utc_now
from app.schemas.video_shot import ShotInput
from app.storage.postgres.shot_list_query import sort_shots_by_shot_no
from app.video.shot_row_mapper import shot_input_to_model


class ShotRepository:
    """分镜持久化。

    参数说明:
        session: postgres_session_scope 提供的 SQLAlchemy Session。
    """

    def __init__(self, session: Session) -> None:
        """绑定数据库 Session。"""
        self._session = session

    def delete_by_project(self, project_id: str) -> int:
        """删除某 project 下全部镜头。"""
        stmt = delete(ShotModel).where(ShotModel.project_id == project_id)
        result = self._session.execute(stmt)
        self._session.commit()
        return int(result.rowcount or 0)

    def insert_shots(
        self,
        project_id: str,
        payloads: list[ShotInput],
        status: str,
    ) -> list[ShotModel]:
        """批量插入镜头。"""
        models = [
            shot_input_to_model(project_id, item, status) for item in payloads
        ]
        self._session.add_all(models)
        self._session.commit()
        for model in models:
            self._session.refresh(model)
        return models

    def list_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 project 下全部镜头（按镜号排序）。"""
        stmt = select(ShotModel).where(ShotModel.project_id == project_id)
        rows = list(self._session.scalars(stmt).all())
        return sort_shots_by_shot_no(rows)

    def list_draft_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 draft 镜头。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status == SHOT_STATUS_DRAFT,
        )
        rows = list(self._session.scalars(stmt).all())
        return sort_shots_by_shot_no(rows)

    def list_entity_validation_pending_by_project(
        self,
        project_id: str,
    ) -> list[ShotModel]:
        """列出待实体校验镜头（draft + rejected）。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status.in_((SHOT_STATUS_DRAFT, SHOT_STATUS_REJECTED)),
        )
        rows = list(self._session.scalars(stmt).all())
        return sort_shots_by_shot_no(rows)

    def list_validated_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 validated 镜头。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status == SHOT_STATUS_VALIDATED,
        )
        return sort_shots_by_shot_no(list(self._session.scalars(stmt).all()))

    def list_rendered_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 rendered 镜头（待 QA）。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status == SHOT_STATUS_RENDERED,
        )
        return sort_shots_by_shot_no(list(self._session.scalars(stmt).all()))

    def list_qa_passed_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 qa_passed 镜头（可合成）。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status == SHOT_STATUS_QA_PASSED,
        )
        return sort_shots_by_shot_no(list(self._session.scalars(stmt).all()))

    def list_awaiting_review_by_project(self, project_id: str) -> list[ShotModel]:
        """列出 awaiting_review 镜头。"""
        stmt = select(ShotModel).where(
            ShotModel.project_id == project_id,
            ShotModel.status == SHOT_STATUS_AWAITING_REVIEW,
        )
        return sort_shots_by_shot_no(list(self._session.scalars(stmt).all()))

    def get_shot(self, shot_id: str) -> ShotModel | None:
        """按 shot_id 查询镜头。"""
        return self._session.get(ShotModel, shot_id)

    def reset_qa_attempts(self, shot_id: str) -> None:
        """清零 QA 重试计数。"""
        model = self._session.get(ShotModel, shot_id)
        if model is None:
            return
        model.qa_attempts = 0
        model.updated_at = utc_now()
        self._session.commit()

    def mark_shots_composed(self, shot_ids: list[str]) -> None:
        """批量将镜头置为 composed。"""
        for shot_id in shot_ids:
            self.update_shot_status(shot_id, SHOT_STATUS_COMPOSED)

    def increment_qa_attempts(self, shot_id: str) -> int:
        """QA 失败计数 +1，返回新值。"""
        model = self._session.get(ShotModel, shot_id)
        if model is None:
            return 0
        model.qa_attempts += 1
        model.updated_at = utc_now()
        self._session.commit()
        return model.qa_attempts

    def update_shot_fields(
        self,
        shot_id: str,
        status: str,
        keyframe_uri: str = "",
    ) -> None:
        """更新镜头状态与关键帧 URI。"""
        model = self._session.get(ShotModel, shot_id)
        if model is None:
            return
        model.status = status
        if keyframe_uri:
            model.keyframe_uri = keyframe_uri
        self._session.commit()

    def update_shot_status(self, shot_id: str, status: str) -> None:
        """更新单镜状态。"""
        model = self._session.get(ShotModel, shot_id)
        if model is None:
            return
        model.status = status
        self._session.commit()

    def commit(self) -> None:
        """提交当前 Session 变更。"""
        self._session.commit()
