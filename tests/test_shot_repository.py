"""ShotRepository 测试（SQLite 内存库）。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.video_constants import SHOT_STATUS_DRAFT
from app.schemas.video_shot import ShotInput
from app.storage.postgres.postgres_metadata import create_all_tables
from app.storage.postgres.shot_repository import ShotRepository


@pytest.fixture()
def session() -> Session:
    """提供 SQLite 内存库 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def _sample_shot() -> ShotInput:
    """构造单条测试镜头。"""
    return ShotInput(
        shot_no="1",
        duration_sec=3,
        shot_size="中景",
        action="推门",
        character_ids=["char_a"],
        scene_id="scene_gate",
    )


def test_insert_and_list_shots(session: Session) -> None:
    """插入后应能按 project 列出。"""
    repository = ShotRepository(session)
    repository.insert_shots("demo", [_sample_shot()], SHOT_STATUS_DRAFT)
    rows = repository.list_by_project("demo")
    assert len(rows) == 1
    assert rows[0].shot_no == "1"
    assert rows[0].status == SHOT_STATUS_DRAFT


def test_replace_deletes_old_shots(session: Session) -> None:
    """delete_by_project 应清空旧数据。"""
    repository = ShotRepository(session)
    repository.insert_shots("demo", [_sample_shot()], SHOT_STATUS_DRAFT)
    removed = repository.delete_by_project("demo")
    assert removed == 1
    assert repository.list_by_project("demo") == []
