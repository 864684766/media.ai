"""道具清单 Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.postgres.prop_inventory_model import PropInventoryModel
from app.models.postgres.time_helper import utc_now
from app.schemas.video_bible import PropInventoryInput
from app.video.bible_row_mapper import prop_input_to_model


class PropInventoryRepository:
    """道具清单读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def upsert_many(
        self,
        project_id: str,
        payloads: list[PropInventoryInput],
    ) -> list[PropInventoryModel]:
        """按 prop_id upsert 多条道具。"""
        saved: list[PropInventoryModel] = []
        for payload in payloads:
            saved.append(self._upsert_one(project_id, payload))
        self._session.commit()
        for row in saved:
            self._session.refresh(row)
        return saved

    def _upsert_one(
        self,
        project_id: str,
        payload: PropInventoryInput,
    ) -> PropInventoryModel:
        """单条 upsert。"""
        existing = self._session.get(PropInventoryModel, (project_id, payload.prop_id))
        if existing is None:
            model = prop_input_to_model(project_id, payload)
            self._session.add(model)
            return model
        existing.name = payload.name
        existing.description = payload.description
        existing.ref_image_urls = list(payload.ref_image_urls)
        existing.updated_at = utc_now()
        return existing

    def list_by_project(self, project_id: str) -> list[PropInventoryModel]:
        """列出 project 下全部道具。"""
        stmt = select(PropInventoryModel).where(
            PropInventoryModel.project_id == project_id,
        )
        return list(self._session.scalars(stmt).all())

    def id_set(self, project_id: str) -> set[str]:
        """返回 prop_id 集合。"""
        return {row.prop_id for row in self.list_by_project(project_id)}

    def delete_one(self, project_id: str, prop_id: str) -> bool:
        """删除单条道具；存在则 True。"""
        model = self._session.get(PropInventoryModel, (project_id, prop_id))
        if model is None:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
