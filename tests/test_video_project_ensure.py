"""video_projects 惰性注册测试。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.video_constants import SHOT_STATUS_DRAFT
from app.schemas.video_shot import ShotInput
from app.services.video_project_list_service import get_video_project_detail
from app.storage.postgres.postgres_metadata import create_all_tables
from app.storage.postgres.shot_repository import ShotRepository


@pytest.fixture()
def session() -> Session:
    """SQLite 内存 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def test_get_detail_auto_registers_namespace_project(session: Session) -> None:
    """有分镜但未建 video_projects 时 GET 详情应惰性注册。"""
    ShotRepository(session).insert_shots(
        "demo",
        [ShotInput(shot_no="1", duration_sec=3)],
        SHOT_STATUS_DRAFT,
    )
    detail = get_video_project_detail(session, "demo")
    assert detail is not None
    assert detail.project.project_id == "demo"
    assert detail.style_bible == ""
