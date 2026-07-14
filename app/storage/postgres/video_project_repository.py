"""video_projects Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.postgres.time_helper import utc_now
from app.models.postgres.video_project_model import VideoProjectModel


class VideoProjectRepository:
    """视频项目 CRUD。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def insert(self, model: VideoProjectModel) -> VideoProjectModel:
        """插入项目。"""
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model

    def get(self, project_id: str) -> VideoProjectModel | None:
        """按 project_id 查询。"""
        return self._session.get(VideoProjectModel, project_id)

    def list_recent(self, limit: int) -> list[VideoProjectModel]:
        """按更新时间倒序列表。"""
        stmt = (
            select(VideoProjectModel)
            .order_by(VideoProjectModel.updated_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt).all())

    def touch_updated(self, project_id: str) -> None:
        """刷新 updated_at（关联数据变更时可选调用）。"""
        row = self.get(project_id)
        if row is None:
            return
        row.updated_at = utc_now()
        self._session.commit()

    def commit(self) -> None:
        """提交当前 Session 变更。"""
        self._session.commit()
