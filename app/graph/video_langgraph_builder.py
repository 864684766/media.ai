"""LangGraph 视频子图组图器（阶段 D1）。

【职责】
    将 validate → review → render → qa → audio → compose 注册为 StateGraph。

【简例】
    graph = build_video_pipeline_graph(session)
    result = graph.invoke(VideoPipelineState(project_id="p1"))
"""

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import BRANCH_PIPELINE_CONTINUE, BRANCH_PIPELINE_PAUSE
from app.graph.video_node_adapters import (
    make_audio_pipeline_adapter,
    make_compose_adapter,
    make_continuity_check_adapter,
    make_render_shots_adapter,
    make_review_gate_adapter,
    make_validate_entities_adapter,
)
from app.graph.video_pipeline_branch_router import (
    route_after_audio_pipeline,
    route_after_continuity_check,
    route_after_review_gate,
)
from app.graph.video_pipeline_constants import (
    NODE_AUDIO_PIPELINE,
    NODE_COMPOSE,
    NODE_CONTINUITY_CHECK,
    NODE_RENDER_SHOTS,
    NODE_REVIEW_GATE,
    NODE_VALIDATE_ENTITIES,
)
from app.schemas.video_pipeline_state import VideoPipelineState


def build_video_pipeline_graph(session: Session):
    """组装视频生产线子图。

    参数:
        session: 单次 run 共用的 PG Session。

    返回:
        CompiledStateGraph: 可 invoke 的子图。
    """
    builder = StateGraph(VideoPipelineState)
    _register_nodes(builder, session)
    _register_edges(builder)
    return builder.compile()


def _register_nodes(builder: StateGraph, session: Session) -> None:
    """注册全部子图节点。"""
    builder.add_node(NODE_VALIDATE_ENTITIES, make_validate_entities_adapter(session))
    builder.add_node(NODE_REVIEW_GATE, make_review_gate_adapter(session))
    builder.add_node(NODE_RENDER_SHOTS, make_render_shots_adapter(session))
    builder.add_node(NODE_CONTINUITY_CHECK, make_continuity_check_adapter(session))
    builder.add_node(NODE_AUDIO_PIPELINE, make_audio_pipeline_adapter(session))
    builder.add_node(NODE_COMPOSE, make_compose_adapter(session))


def _register_edges(builder: StateGraph) -> None:
    """注册顺序边与 HITL 条件边。"""
    builder.add_edge(START, NODE_VALIDATE_ENTITIES)
    builder.add_edge(NODE_VALIDATE_ENTITIES, NODE_REVIEW_GATE)
    builder.add_conditional_edges(
        NODE_REVIEW_GATE,
        route_after_review_gate,
        {BRANCH_PIPELINE_CONTINUE: NODE_RENDER_SHOTS, BRANCH_PIPELINE_PAUSE: END},
    )
    builder.add_edge(NODE_RENDER_SHOTS, NODE_CONTINUITY_CHECK)
    builder.add_conditional_edges(
        NODE_CONTINUITY_CHECK,
        route_after_continuity_check,
        {BRANCH_PIPELINE_CONTINUE: NODE_AUDIO_PIPELINE, BRANCH_PIPELINE_PAUSE: END},
    )
    builder.add_conditional_edges(
        NODE_AUDIO_PIPELINE,
        route_after_audio_pipeline,
        {BRANCH_PIPELINE_CONTINUE: NODE_COMPOSE, BRANCH_PIPELINE_PAUSE: END},
    )
    builder.add_edge(NODE_COMPOSE, END)
