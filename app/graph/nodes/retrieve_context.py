"""retrieve_context 节点（检索链薄封装）。

【职责】
    route_question 判定 needs_project / needs_web 为 true 时执行，
    调用 app/retrieval/retrieval_pipeline.py 产出证据，写入 state.retrieval。
    节点本身不含检索逻辑（节点与实现分离，见 sec-09）。

【当前节点粒度说明】
    设计稿把检索链拆为 retrieve_hybrid / grader / rerank / web_search 多个节点；
    当前实现先用单个 retrieve_context 节点封装整条流水线（Grader 回环在
    流水线内部完成），后续需要 LangGraph 级回环时再拆分，接口不变。
"""

from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.agent_state import AgentState


def retrieve_context_node(
    state: AgentState,
    pipeline: RetrievalPipeline | None = None,
) -> AgentState:
    """执行检索流水线并写入证据。

    参数:
        state: 当前图状态（route 必须已由 route_question 写入）。
        pipeline: 检索流水线；None 时跳过检索（无库环境安全降级）。

    返回:
        AgentState: 写入 retrieval 后的新状态。
    """
    if pipeline is None or state.route is None:
        return state
    context = pipeline.run(
        question=state.question,
        route=state.route,
        project_id=state.project_id,
        runtime_config=state.runtime_config,
    )
    return state.model_copy(update={"retrieval": context})
