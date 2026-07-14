"""视频子图一键运行服务（阶段 D1）。

【职责】
    在单 PG Session 内 invoke LangGraph 视频子图，串联既有业务服务。

【何时调用】
    POST /api/v1/video/projects/{project_id}/pipeline/run
"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import PIPELINE_RUN_COMPLETED
from app.graph.video_langgraph_builder import build_video_pipeline_graph
from app.schemas.video_pipeline_run import VideoPipelineRunResponse
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.video_pipeline_run_mapper import map_pipeline_run_response


def run_video_pipeline(session: Session, project_id: str) -> VideoPipelineRunResponse:
    """执行视频生产线子图。

    参数:
        session: PG Session。
        project_id: 项目 id。

    返回:
        VideoPipelineRunResponse: 运行结果与暂停原因。
    """
    graph = build_video_pipeline_graph(session)
    initial = VideoPipelineState(project_id=project_id, run_status=PIPELINE_RUN_COMPLETED)
    result = graph.invoke(initial)
    state = _coerce_state(result)
    return map_pipeline_run_response(state)


def _coerce_state(result: VideoPipelineState | dict) -> VideoPipelineState:
    """将 invoke 结果规范为 VideoPipelineState。"""
    if isinstance(result, VideoPipelineState):
        return result
    return VideoPipelineState.model_validate(result)
