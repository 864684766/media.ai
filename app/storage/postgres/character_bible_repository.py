"""角色圣经 Repository。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.postgres.character_bible_model import CharacterBibleModel
from app.models.postgres.time_helper import utc_now
from app.schemas.video_bible import CharacterBibleInput
from app.video.bible_row_mapper import character_input_to_model


class CharacterBibleRepository:
    """角色圣经读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def upsert_many(
        self,
        project_id: str,
        payloads: list[CharacterBibleInput],
    ) -> list[CharacterBibleModel]:
        """按 character_id upsert 多条角色。"""
        saved: list[CharacterBibleModel] = []
        for payload in payloads:
            saved.append(self._upsert_one(project_id, payload))
        self._session.commit()
        for row in saved:
            self._session.refresh(row)
        return saved

    def _upsert_one(
        self,
        project_id: str,
        payload: CharacterBibleInput,
    ) -> CharacterBibleModel:
        """单条 upsert 内部实现。"""
        existing = self._get(project_id, payload.character_id)
        if existing is None:
            model = character_input_to_model(project_id, payload, lock_version=1)
            self._session.add(model)
            return model
        self._apply_update(existing, payload)
        return existing

    def get_character(self, project_id: str, character_id: str) -> CharacterBibleModel | None:
        """按联合主键查询角色。"""
        return self._get(project_id, character_id)

    def _get(self, project_id: str, character_id: str) -> CharacterBibleModel | None:
        """按联合主键查询。"""
        key = (project_id, character_id)
        return self._session.get(CharacterBibleModel, key)

    def _apply_update(
        self,
        model: CharacterBibleModel,
        payload: CharacterBibleInput,
    ) -> None:
        """更新已有角色并递增 lock_version。"""
        model.name = payload.name
        model.appearance = payload.appearance
        model.costume = payload.costume
        model.age_band = payload.age_band
        model.ref_image_urls = list(payload.ref_image_urls)
        model.voice_id = payload.voice_id
        model.lock_version = model.lock_version + 1
        model.updated_at = utc_now()

    def list_by_project(self, project_id: str) -> list[CharacterBibleModel]:
        """列出 project 下全部角色。"""
        stmt = select(CharacterBibleModel).where(
            CharacterBibleModel.project_id == project_id,
        )
        return list(self._session.scalars(stmt).all())

    def id_set(self, project_id: str) -> set[str]:
        """返回 project 下全部 character_id 集合。"""
        return {row.character_id for row in self.list_by_project(project_id)}

    def delete_one(self, project_id: str, character_id: str) -> bool:
        """删除单条角色；存在则 True。"""
        model = self._get(project_id, character_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
