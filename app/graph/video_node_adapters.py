"""视频子图 LangGraph 节点适配器（绑定 Session）。"""

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.graph.video_nodes.audio_pipeline_node import run_audio_pipeline_step
from app.graph.video_nodes.compose_node import run_compose_step
from app.graph.video_nodes.continuity_check_node import run_continuity_check_step
from app.graph.video_nodes.render_shots_node import run_render_shots_step
from app.graph.video_nodes.review_gate_node import run_review_gate_step
from app.graph.video_nodes.validate_entities_node import run_validate_entities_step
from app.schemas.video_pipeline_state import VideoPipelineState

VideoGraphNode = Callable[[VideoPipelineState], dict]


def make_validate_entities_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 validate 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_validate_entities_step(session, state)
    return adapter


def make_review_gate_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 review_gate 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_review_gate_step(session, state)
    return adapter


def make_render_shots_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 render 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_render_shots_step(session, state)
    return adapter


def make_continuity_check_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 QA 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_continuity_check_step(session, state)
    return adapter


def make_audio_pipeline_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 audio 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_audio_pipeline_step(session, state)
    return adapter


def make_compose_adapter(session: Session) -> VideoGraphNode:
    """绑定 Session 的 compose 适配器。"""
    def adapter(state: VideoPipelineState) -> dict:
        return run_compose_step(session, state)
    return adapter
