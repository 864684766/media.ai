"""场景锁定 Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.postgres.scene_lock_model import SceneLockModel
from app.models.postgres.time_helper import utc_now
from app.schemas.video_bible import SceneLockInput
from app.video.bible_row_mapper import scene_input_to_model


class SceneLockRepository:
    """场景锁定读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def upsert_many(
        self,
        project_id: str,
        payloads: list[SceneLockInput],
    ) -> list[SceneLockModel]:
        """按 scene_id upsert 多条场景。"""
        saved: list[SceneLockModel] = []
        for payload in payloads:
            saved.append(self._upsert_one(project_id, payload))
        self._session.commit()
        for row in saved:
            self._session.refresh(row)
        return saved

    def _upsert_one(self, project_id: str, payload: SceneLockInput) -> SceneLockModel:
        """单条 upsert。"""
        existing = self._session.get(SceneLockModel, (project_id, payload.scene_id))
        if existing is None:
            model = scene_input_to_model(project_id, payload)
            self._session.add(model)
            return model
        existing.name = payload.name
        existing.setting = payload.setting
        existing.lighting = payload.lighting
        existing.ref_image_urls = list(payload.ref_image_urls)
        existing.updated_at = utc_now()
        return existing

    def list_by_project(self, project_id: str) -> list[SceneLockModel]:
        """列出 project 下全部场景。"""
        stmt = select(SceneLockModel).where(SceneLockModel.project_id == project_id)
        return list(self._session.scalars(stmt).all())

    def id_set(self, project_id: str) -> set[str]:
        """返回 scene_id 集合。"""
        return {row.scene_id for row in self.list_by_project(project_id)}

    def delete_one(self, project_id: str, scene_id: str) -> bool:
        """删除单条场景；存在则 True。"""
        model = self._session.get(SceneLockModel, (project_id, scene_id))
        if model is None:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
