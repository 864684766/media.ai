"""策划→分镜 API 测试（阶段 G2）。"""

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.api_constants import CREATIVE_ROUTE_PREFIX
from app.core.creative_plan_constants import PLAN_STATUS_APPROVED, PLAN_STATUS_AWAITING_REVIEW
from app.core.creation_type_constants import CREATION_TYPE_VIDEO
from app.schemas.creative_plan import VideoPlanContent, VideoSegmentItem
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_storyboard_client(monkeypatch) -> TestClient:
    """SQLite 内存库 TestClient（大纲→分镜）。"""
    from app.application import create_app

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)

    class _SessionScope:
        """模拟 postgres_session_scope。"""

        def __enter__(self):
            self._session = factory()
            return self._session

        def __exit__(self, *args):
            self._session.close()

    def _scope():
        return _SessionScope()

    monkeypatch.setattr("app.api.creative_plans.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.creative_plans.postgres_session_scope", _scope)
    return TestClient(create_app())


def _seed_approved_video_plan(client: TestClient, project_id: str) -> str:
    """向测试库插入一条 approved 视频大纲。"""
    from app.api import creative_plans as cp_module
    from app.models.postgres.creative_plan_model import CreativePlanModel
    from app.models.postgres.time_helper import utc_now

    with cp_module.postgres_session_scope() as session:
        content = VideoPlanContent(
            hook="产品特写开场",
            segments=[
                VideoSegmentItem(start_sec=0, end_sec=10, visual="产品旋转", mood="期待"),
                VideoSegmentItem(start_sec=10, end_sec=30, visual="功能演示", mood="上扬"),
            ],
            target_duration_sec=30,
        )
        now = utc_now()
        plan_id = str(uuid4())
        row = CreativePlanModel(
            plan_id=plan_id,
            conversation_id=str(uuid4()),
            project_id=project_id,
            creation_type=CREATION_TYPE_VIDEO,
            status=PLAN_STATUS_APPROVED,
            version=1,
            title="测试视频方案",
            content_json=json.dumps(content.model_dump(), ensure_ascii=False),
            content_md="## 开场\n产品特写",
            clarification_session_id=None,
            created_at=now,
            updated_at=now,
            approved_at=now,
        )
        session.add(row)
        session.commit()
        return plan_id


def test_plan_storyboard_requires_approved(pg_storyboard_client: TestClient) -> None:
    """未确认大纲应 409。"""
    from app.api import creative_plans as cp_module
    from app.models.postgres.creative_plan_model import CreativePlanModel
    from app.models.postgres.time_helper import utc_now

    project_id = "proj-draft"

    with cp_module.postgres_session_scope() as session:
        plan_id = str(uuid4())
        now = utc_now()
        session.add(
            CreativePlanModel(
                plan_id=plan_id,
                conversation_id=str(uuid4()),
                project_id=project_id,
                creation_type=CREATION_TYPE_VIDEO,
                status=PLAN_STATUS_AWAITING_REVIEW,
                version=1,
                title="待审",
                content_json="{}",
                content_md="草案",
                created_at=now,
                updated_at=now,
            ),
        )
        session.commit()
    response = pg_storyboard_client.post(f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans/{plan_id}/storyboard")
    assert response.status_code == 409


def test_plan_storyboard_from_approved_video_plan(
    pg_storyboard_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """已确认视频大纲应生成并入库分镜（模板 fallback）。"""
    monkeypatch.setattr(
        "app.services.plan_storyboard_shot_source.run_plan_storyboard_llm",
        lambda *_args, **_kwargs: "",
    )
    project_id = "proj-video-01"
    plan_id = _seed_approved_video_plan(pg_storyboard_client, project_id)
    response = pg_storyboard_client.post(
        f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans/{plan_id}/storyboard",
        json={"project_id": project_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["plan_id"] == plan_id
    assert body["project_id"] == project_id
    assert len(body["shots"]) >= 2
    assert body["shots"][0]["shot_no"] == "1"
