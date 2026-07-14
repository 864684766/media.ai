"""bible Repository 与实体校验测试。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.video_constants import SHOT_STATUS_DRAFT, SHOT_STATUS_REJECTED
from app.schemas.video_bible import CharacterBibleInput, PropInventoryInput, SceneLockInput
from app.schemas.video_shot import ShotInput
from app.services.entity_validation_service import validate_project_entities
from app.storage.postgres.character_bible_repository import CharacterBibleRepository
from app.storage.postgres.postgres_metadata import create_all_tables
from app.storage.postgres.prop_inventory_repository import PropInventoryRepository
from app.storage.postgres.scene_lock_repository import SceneLockRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.entity_validation_checker import BibleIdSets, collect_shot_validation_reasons


@pytest.fixture()
def session() -> Session:
    """SQLite 内存 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def test_character_bible_upsert_increments_lock_version(session: Session) -> None:
    """二次 upsert 应递增 lock_version。"""
    repo = CharacterBibleRepository(session)
    payload = CharacterBibleInput(character_id="char_a", name="甲")
    repo.upsert_many("demo", [payload])
    repo.upsert_many("demo", [CharacterBibleInput(character_id="char_a", name="甲改")])
    row = repo.list_by_project("demo")[0]
    assert row.lock_version == 2
    assert row.name == "甲改"


def test_validate_passes_when_bible_complete(session: Session) -> None:
    """bible 齐全时 draft 镜头应变 validated。"""
    CharacterBibleRepository(session).upsert_many(
        "demo",
        [CharacterBibleInput(character_id="char_a", name="甲")],
    )
    SceneLockRepository(session).upsert_many(
        "demo",
        [SceneLockInput(scene_id="scene_a", name="场景")],
    )
    ShotRepository(session).insert_shots(
        "demo",
        [
            ShotInput(
                shot_no="1",
                duration_sec=3,
                character_ids=["char_a"],
                scene_id="scene_a",
            ),
        ],
        SHOT_STATUS_DRAFT,
    )
    result = validate_project_entities(session, "demo")
    assert result.validated_count == 1
    assert result.rejected_count == 0


def test_collect_reasons_for_missing_scene() -> None:
    """缺失场景 ID 应产生 missing_scene 原因。"""
    from app.models.postgres.shot_model import ShotModel

    shot = ShotModel(
        shot_id="s1",
        project_id="demo",
        shot_no="1",
        duration_sec=3,
        scene_id="scene_missing",
    )
    reasons = collect_shot_validation_reasons(
        shot,
        BibleIdSets(character_ids=set(), scene_ids={"scene_a"}, prop_ids=set()),
    )
    assert any("missing_scene" in r for r in reasons)


def test_validate_revalidates_rejected_shots(session: Session) -> None:
    """rejected 镜头在 bible 补全后应能重新通过校验。"""
    shot_repo = ShotRepository(session)
    shot_repo.insert_shots(
        "demo",
        [
            ShotInput(
                shot_no="1",
                duration_sec=3,
                prop_ids=["prop_missing"],
            ),
        ],
        SHOT_STATUS_REJECTED,
    )
    first = validate_project_entities(session, "demo")
    assert first.validated_count == 0
    assert first.rejected_count == 1
    PropInventoryRepository(session).upsert_many(
        "demo",
        [PropInventoryInput(prop_id="prop_missing", name="道具")],
    )
    second = validate_project_entities(session, "demo")
    assert second.validated_count == 1
    assert second.rejected_count == 0
