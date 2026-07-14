"""VideoPipelineState → API 响应映射。"""

from app.schemas.video_compose import ComposeOutputUrls
from app.schemas.video_pipeline_run import VideoPipelineRunResponse
from app.schemas.video_pipeline_state import VideoPipelineState
from app.video.compose_output_url_builder import build_compose_download_url, build_compose_open_url
from app.video.subtitle_burn_eligibility import resolve_subtitles_burned_flag


def map_pipeline_run_response(state: VideoPipelineState) -> VideoPipelineRunResponse:
    """将子图终态映射为 REST 响应。

    参数:
        state: invoke 后的子图状态。

    返回:
        VideoPipelineRunResponse: POST pipeline/run 响应体。
    """
    compose_output = _resolve_compose_output(state)
    return VideoPipelineRunResponse(
        project_id=state.project_id,
        run_status=state.run_status,
        current_step=state.current_step,
        steps_completed=state.steps_completed,
        paused=state.paused,
        pause_reason=state.pause_reason,
        validate_validated_count=state.validate_validated_count,
        render_job_id=state.render_job_id,
        qa_passed_count=state.qa_passed_count,
        qa_awaiting_count=state.qa_awaiting_count,
        compose_output=compose_output,
        error_message=state.error_message,
    )


def _resolve_compose_output(state: VideoPipelineState) -> ComposeOutputUrls | None:
    """有成片 URI 时构造 ComposeOutputUrls。"""
    uri = state.compose_output_uri
    if not uri:
        return None
    return ComposeOutputUrls(
        uri=uri,
        open_url=build_compose_open_url(uri),
        download_url=build_compose_download_url(uri),
        subtitles_burned=resolve_subtitles_burned_flag(state.project_id, uri),
    )
