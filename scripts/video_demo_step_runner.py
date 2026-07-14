"""视频 E2E 演示单步执行器。

【职责】
    run_video_demo.py 各阶段调用对应 service，保持单步可测。

【简例】
    with session: run_demo_storyboard(session, project_id)
"""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.schemas.video_bible import (
    CharacterBibleInput,
    CharacterBibleUpsertRequest,
    PropInventoryInput,
    PropInventoryUpsertRequest,
    SceneLockInput,
    SceneLockUpsertRequest,
)
from app.schemas.video_project import VideoProjectCreateRequest
from app.schemas.video_shot import ShotInput, StoryboardSubmitRequest
from app.services.audio_pipeline_service import run_audio_pipeline
from app.services.bible_service import upsert_characters, upsert_props, upsert_scenes
from app.services.compose_job_service import ComposeBlockedError, start_compose_job
from app.services.continuity_qa_service import run_continuity_qa
from app.services.entity_validation_service import validate_project_entities
from app.services.render_job_service import start_render_job
from app.services.storyboard_service import submit_storyboard
from app.services.video_project_create_service import ProjectIdConflictError, create_video_project
from app.video.storyboard_json_parser import parse_storyboard_json_array


def ensure_demo_project(session: Session, project_id: str) -> None:
    """确保 video_projects 存在（已存在则跳过）。"""
    body = VideoProjectCreateRequest(title="E2E 演示短片", project_id=project_id)
    try:
        create_video_project(session, body)
    except ProjectIdConflictError:
        return None


def run_demo_storyboard(session: Session, project_id: str, fixture: Path) -> dict:
    """提交 fixture 分镜并返回响应 dict。"""
    raw = fixture.read_text(encoding="utf-8")
    rows = parse_storyboard_json_array(raw)
    shots = [ShotInput.model_validate(row) for row in rows]
    response = submit_storyboard(session, project_id, StoryboardSubmitRequest(shots=shots))
    return response.model_dump()


def run_demo_bible(session: Session, project_id: str, fixture: Path) -> None:
    """upsert demo bible 三类实体。"""
    data = json.loads(fixture.read_text(encoding="utf-8"))
    _upsert_characters(session, project_id, data)
    _upsert_scenes(session, project_id, data)
    _upsert_props(session, project_id, data)


def run_demo_validate(session: Session, project_id: str) -> dict:
    """校验分镜实体引用。"""
    return validate_project_entities(session, project_id).model_dump()


def run_demo_render(session: Session, project_id: str) -> dict:
    """启动渲染 Job。"""
    return start_render_job(session, project_id).model_dump()


def run_demo_qa(session: Session, project_id: str) -> dict:
    """运行连续性 QA。"""
    return run_continuity_qa(session, project_id).model_dump()


def run_demo_audio(session: Session, project_id: str) -> dict:
    """生成对白轨与字幕。"""
    return run_audio_pipeline(session, project_id).model_dump()


def run_demo_compose(session: Session, project_id: str) -> dict:
    """合成时间轴成片。"""
    return start_compose_job(session, project_id).model_dump()


def _upsert_characters(session: Session, project_id: str, data: dict) -> None:
    """写入角色圣经。"""
    items = data.get("characters") or []
    if not items:
        return
    req = CharacterBibleUpsertRequest(
        characters=[CharacterBibleInput.model_validate(x) for x in items],
    )
    upsert_characters(session, project_id, req)


def _upsert_scenes(session: Session, project_id: str, data: dict) -> None:
    """写入场景锁定。"""
    items = data.get("scenes") or []
    if not items:
        return
    req = SceneLockUpsertRequest(scenes=[SceneLockInput.model_validate(x) for x in items])
    upsert_scenes(session, project_id, req)


def _upsert_props(session: Session, project_id: str, data: dict) -> None:
    """写入道具清单。"""
    items = data.get("props") or []
    if not items:
        return
    req = PropInventoryUpsertRequest(props=[PropInventoryInput.model_validate(x) for x in items])
    upsert_props(session, project_id, req)
