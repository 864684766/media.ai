"""视频子图 audio_pipeline 节点。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import PAUSE_REASON_AWAITING_BGM
from app.graph.video_nodes.audio_pipeline_bgm_pause_helper import should_pause_for_bgm_before_compose
from app.graph.video_pipeline_constants import NODE_AUDIO_PIPELINE
from app.graph.video_pipeline_pause_patch_builder import build_pipeline_pause_patch
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.audio_pipeline_service import run_audio_pipeline


def run_audio_pipeline_step(session: Session, state: VideoPipelineState) -> dict:
    """生成对白 TTS 与字幕 SRT；可选在合成前暂停等待 BGM。"""
    run_audio_pipeline(session, state.project_id)
    completed = [*state.steps_completed, NODE_AUDIO_PIPELINE]
    if should_pause_for_bgm_before_compose():
        return build_pipeline_pause_patch(
            NODE_AUDIO_PIPELINE,
            PAUSE_REASON_AWAITING_BGM,
            completed,
        )
    return {
        "current_step": NODE_AUDIO_PIPELINE,
        "steps_completed": completed,
    }
