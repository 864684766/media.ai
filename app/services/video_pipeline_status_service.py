"""视频流水线状态查询服务。"""

from sqlalchemy.orm import Session

from app.schemas.video_pipeline import PipelineStatusResponse, PipelineStepOutput
from app.schemas.video_shot import ShotOutput
from app.storage.postgres.shot_repository import ShotRepository
from app.storage.postgres.video_pipeline_job_repository import VideoPipelineJobRepository
from app.video.pipeline_blocking_reason_resolver import resolve_pipeline_blocking_reason
from app.video.pipeline_status_aggregator import aggregate_status_counts
from app.video.pipeline_step_catalog import build_pipeline_steps
from app.video.shot_row_mapper import shot_model_to_output
from app.video.video_review_config_reader import load_video_review_config


def get_pipeline_status(session: Session, project_id: str) -> PipelineStatusResponse:
    """汇总 project 流水线进度与待审镜头。"""
    repo = ShotRepository(session)
    shots = repo.list_by_project(project_id)
    counts = aggregate_status_counts(shots)
    awaiting = repo.list_awaiting_review_by_project(project_id)
    review_cfg = load_video_review_config()
    latest_job = VideoPipelineJobRepository(session).get_latest_job_for_project(project_id)
    return PipelineStatusResponse(
        project_id=project_id,
        shots_total=len(shots),
        status_counts=counts,
        steps=_map_steps(build_pipeline_steps(counts)),
        awaiting_review=[shot_model_to_output(s) for s in awaiting],
        review_config={
            "storyboard": review_cfg.storyboard_enabled,
            "keyframe": review_cfg.keyframe_enabled,
        },
        blocking_reason=resolve_pipeline_blocking_reason(len(shots), counts),
        latest_job_id=latest_job.job_id if latest_job else "",
    )


def _map_steps(raw_steps: list[dict]) -> list[PipelineStepOutput]:
    """dict 步骤转响应模型。"""
    return [PipelineStepOutput(**item) for item in raw_steps]
