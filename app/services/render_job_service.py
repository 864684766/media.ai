"""V3/V7 渲染 Job 业务服务。"""

from sqlalchemy.orm import Session

from app.core.video_constants import (
    ASSET_TYPE_CLIP,
    ASSET_TYPE_KEYFRAME,
    SHOT_STATUS_RENDERED,
    SHOT_STATUS_RENDERING,
)
from app.schemas.video_render import RenderJobOutput, RenderStartResponse, ShotAssetOutput
from app.storage.postgres.render_job_repository import RenderJobRepository
from app.storage.postgres.shot_asset_repository import ShotAssetRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.clip_render_dispatcher import dispatch_clip_render
from app.video.keyframe_render_dispatcher import dispatch_keyframe_render
from app.video.project_budget_gate import BudgetExceededError, assert_budget_allows
from app.video.shot_render_cost_calculator import calculate_shots_clip_cost
from app.video.video_budget_config_reader import load_video_budget_config
from app.video.video_provider_config_reader import (
    load_video_provider_config,
    lookup_provider_capability,
)


def start_render_job(session: Session, project_id: str) -> RenderStartResponse:
    """对 validated 镜头执行渲染并返回 Job。"""
    shot_repo = ShotRepository(session)
    shots = shot_repo.list_validated_by_project(project_id)
    provider_cfg = load_video_provider_config()
    _guard_render_budget(session, project_id, shots, provider_cfg)
    job_repo = RenderJobRepository(session)
    job = job_repo.create_job(project_id, len(shots))
    job_repo.mark_running(job)
    assets = _render_all_shots(session, shot_repo, job_repo, job, shots, provider_cfg)
    job_repo.mark_completed(job)
    refreshed = job_repo.get_job(job.job_id)
    assert refreshed is not None
    return RenderStartResponse(job=_job_output(refreshed), assets=assets)


def get_render_job(session: Session, job_id: str) -> RenderJobOutput | None:
    """查询 Job 状态。"""
    job = RenderJobRepository(session).get_job(job_id)
    if job is None:
        return None
    return _job_output(job)


def _guard_render_budget(session, project_id, shots, provider_cfg) -> None:
    """渲染前预算熔断。"""
    budget = load_video_budget_config()
    if not budget.fuse_on_render:
        return
    cap = lookup_provider_capability(provider_cfg, provider_cfg.active_clip)
    estimate = calculate_shots_clip_cost(shots, cap)
    assert_budget_allows(session, project_id, budget, estimate)


def _render_all_shots(session, shot_repo, job_repo, job, shots, provider_cfg) -> list:
    """逐镜渲染。"""
    asset_repo = ShotAssetRepository(session)
    outputs: list[ShotAssetOutput] = []
    for shot in shots:
        outputs.extend(_render_one_shot(shot_repo, asset_repo, job_repo, job, shot, provider_cfg))
    return outputs


def _render_one_shot(shot_repo, asset_repo, job_repo, job, shot, provider_cfg) -> list:
    """渲染单镜并更新状态。"""
    shot_repo.update_shot_fields(shot.shot_id, SHOT_STATUS_RENDERING)
    frame_uri, frame_provider = dispatch_keyframe_render(shot, provider_cfg)
    clip_uri, last_frame, clip_provider, clip_cost = dispatch_clip_render(shot, provider_cfg)
    frame_row = asset_repo.insert_asset(
        shot.shot_id, shot.project_id, ASSET_TYPE_KEYFRAME, frame_uri, provider=frame_provider,
    )
    clip_row = asset_repo.insert_asset(
        shot.shot_id, shot.project_id, ASSET_TYPE_CLIP, clip_uri, last_frame,
        provider=clip_provider, cost=clip_cost,
    )
    shot_repo.update_shot_fields(shot.shot_id, SHOT_STATUS_RENDERED, frame_uri)
    job_repo.increment_finished(job)
    return [_asset_output(frame_row), _asset_output(clip_row)]


def _job_output(job) -> RenderJobOutput:
    """ORM Job 转响应。"""
    return RenderJobOutput(
        job_id=job.job_id,
        project_id=job.project_id,
        status=job.status,
        total_shots=job.total_shots,
        finished_shots=job.finished_shots,
    )


def _asset_output(row) -> ShotAssetOutput:
    """资产行转响应（含 open/download URL）。"""
    rel = row.uri
    base = f"/api/v1/files/video/{rel}"
    return ShotAssetOutput(
        asset_id=row.asset_id,
        shot_id=row.shot_id,
        asset_type=row.asset_type,
        uri=rel,
        provider=row.provider,
        cost=row.cost,
        open_url=f"{base}?disposition=inline",
        download_url=f"{base}?disposition=attachment",
    )
