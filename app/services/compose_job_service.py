"""视频合成 Job 业务服务（V5/V7/V8）。"""

import json

from sqlalchemy.orm import Session

from app.schemas.video_compose import ComposeJobOutput, ComposeOutputUrls, ComposeStartResponse
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.storage.postgres.compose_job_repository import ComposeJobRepository
from app.storage.postgres.shot_asset_repository import ShotAssetRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.audio_output_path_helper import subtitle_relative_uri
from app.video.compose_eligibility_checker import collect_compose_block_reasons
from app.video.compose_output_dispatcher import dispatch_compose_output
from app.video.compose_output_url_builder import (
    build_compose_download_url,
    build_compose_open_url,
)
from app.video.compose_timeline_audio_builder import build_audio_track_entries
from app.video.compose_timeline_builder import build_timeline_payload, timeline_to_json
from app.video.project_budget_gate import assert_budget_allows
from app.video.subtitle_burn_eligibility import resolve_subtitles_burned_flag
from app.video.video_budget_config_reader import load_video_budget_config
from app.video.video_provider_config_reader import load_video_provider_config


class ComposeBlockedError(Exception):
    """无 qa_passed 镜头等阻断合成。"""

    def __init__(self, reasons: list[str]) -> None:
        """保存阻断原因。"""
        self.reasons = reasons
        super().__init__(reasons[0] if reasons else "compose blocked")


def start_compose_job(session: Session, project_id: str) -> ComposeStartResponse:
    """将 qa_passed 镜头合成时间轴产物。"""
    shot_repo = ShotRepository(session)
    shots = shot_repo.list_qa_passed_by_project(project_id)
    blockers = collect_compose_block_reasons(shots)
    if blockers:
        raise ComposeBlockedError(blockers)
    _guard_compose_budget(session, project_id)
    job_repo = ComposeJobRepository(session)
    job = job_repo.create_job(project_id, len(shots))
    job_repo.mark_running(job)
    output = _write_timeline(session, project_id, job.job_id, shots)
    job_repo.mark_completed(
        job,
        output["uri"],
        output["json"],
        output.get("subtitle_uri", ""),
        output.get("audio_tracks_json", ""),
    )
    shot_repo.mark_shots_composed([s.shot_id for s in shots])
    refreshed = job_repo.get_job(job.job_id)
    assert refreshed is not None
    return ComposeStartResponse(job=_job_output(refreshed), output=output["urls"])


def get_compose_job(session: Session, job_id: str) -> ComposeJobOutput | None:
    """查询合成 Job。"""
    job = ComposeJobRepository(session).get_job(job_id)
    if job is None:
        return None
    return _job_output(job)


def _guard_compose_budget(session, project_id: str) -> None:
    """合成前预算熔断（合成本身零成本占位）。"""
    budget = load_video_budget_config()
    if not budget.fuse_on_compose:
        return
    assert_budget_allows(session, project_id, budget, 0.0)


def _write_timeline(session, project_id, job_id, shots) -> dict:
    """构建并落盘时间轴或 mp4。"""
    asset_repo = ShotAssetRepository(session)
    audio_repo = AudioAssetRepository(session)
    clip_map = {s.shot_id: asset_repo.find_clip_uri(s.shot_id) for s in shots}
    clip_uris = [clip_map[s.shot_id] for s in shots]
    audio_tracks = build_audio_track_entries(audio_repo.list_by_project(project_id))
    subtitle_uri = subtitle_relative_uri(project_id)
    payload = build_timeline_payload(
        project_id, job_id, shots, clip_map, audio_tracks, subtitle_uri,
    )
    provider_cfg = load_video_provider_config()
    uri = dispatch_compose_output(project_id, payload, clip_uris, provider_cfg)
    return {
        "uri": uri,
        "json": timeline_to_json(payload),
        "urls": _output_urls(project_id, uri),
        "subtitle_uri": subtitle_uri,
        "audio_tracks_json": json.dumps(audio_tracks, ensure_ascii=False),
    }


def _output_urls(project_id: str, relative_uri: str) -> ComposeOutputUrls:
    """构造 open/download URL 与字幕烧录标记。"""
    burned = resolve_subtitles_burned_flag(project_id, relative_uri)
    return ComposeOutputUrls(
        uri=relative_uri,
        open_url=build_compose_open_url(relative_uri),
        download_url=build_compose_download_url(relative_uri),
        subtitles_burned=burned,
    )


def _job_output(job) -> ComposeJobOutput:
    """ORM 转响应。"""
    urls = _output_urls(job.project_id, job.output_uri) if job.output_uri else None
    return ComposeJobOutput(
        job_id=job.job_id,
        project_id=job.project_id,
        status=job.status,
        total_shots=job.total_shots,
        output_uri=job.output_uri,
        output=urls,
    )
