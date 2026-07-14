"""LangGraph 节点适配器。

【职责】
    把项目已有的节点函数（签名带 repository/responder 等注入参数）
    包装成 LangGraph 要求的标准节点签名：state -> 字段更新 dict。

【为什么需要适配】
    LangGraph 节点只能收 state 一个参数；而 repository（数据库）、
    responder（测试注入的生成函数）属于"每次组图时确定"的依赖，
    因此用闭包工厂（make_*_adapter）在组图时绑定，运行时只传 state。

【简例】
    adapter = make_load_history_adapter(repository)
    update = adapter(state)          # -> {"history": [...]}
"""

from collections.abc import Callable

from app.graph.route_classifiers import RouteClassifiers
from app.graph.nodes.compact_history import compact_history_node
from app.graph.nodes.generate import Responder, generate_node
from app.graph.nodes.load_history import load_history_node
from app.graph.nodes.load_skill import load_skill_node
from app.graph.nodes.retrieve_context import retrieve_context_node
from app.graph.nodes.route_question import route_question_node
from app.graph.nodes.save_messages import save_messages_node
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.agent_state import AgentState
from app.storage.postgres.conversation_repository import ConversationRepository

# LangGraph 节点的标准签名：输入 state，输出「本节点写入的字段」dict
GraphNode = Callable[[AgentState], dict]


def load_skill_adapter(state: AgentState) -> dict:
    """load_skill 节点适配器。

    参数:
        state: 当前图状态（skill_id 从 state.requested_skill_id 读取）。

    返回:
        dict: {"skill": SkillContext}，LangGraph 将其合并进 state。
    """
    new_state = load_skill_node(state, skill_id=state.requested_skill_id)
    return {"skill": new_state.skill}


def make_load_history_adapter(
    repository: ConversationRepository | None,
) -> GraphNode:
    """构造 load_history 节点适配器（绑定 repository）。

    参数:
        repository: 可选 PG Repository；为空时 history 保持为空列表。

    返回:
        GraphNode: 标准 LangGraph 节点函数。
    """

    def adapter(state: AgentState) -> dict:
        """读取会话历史并返回 history 字段更新。"""
        new_state = load_history_node(state, repository=repository)
        return {"history": new_state.history}

    return adapter


def make_route_question_adapter(
    classifiers: RouteClassifiers | None,
) -> GraphNode:
    """构造 route_question 节点适配器（绑定路由分类器包）。

    参数:
        classifiers: 可选 L2/L3 分类器；None 时纯规则层。

    返回:
        GraphNode: 标准 LangGraph 节点函数。
    """

    def adapter(state: AgentState) -> dict:
        """执行路由级联并返回 route 字段更新。"""
        new_state = route_question_node(state, classifiers=classifiers)
        return {"route": new_state.route}

    return adapter


def make_retrieve_context_adapter(pipeline: RetrievalPipeline | None) -> GraphNode:
    """构造 retrieve_context 节点适配器（绑定检索流水线）。

    参数:
        pipeline: 检索流水线；None 时节点跳过检索（无库环境安全降级）。

    返回:
        GraphNode: 标准 LangGraph 节点函数。
    """

    def adapter(state: AgentState) -> dict:
        """执行检索链并返回 retrieval 字段更新。"""
        new_state = retrieve_context_node(state, pipeline=pipeline)
        return {"retrieval": new_state.retrieval}

    return adapter


def compact_history_adapter(state: AgentState) -> dict:
    """compact_history 节点适配器。

    参数:
        state: 当前图状态。

    返回:
        dict: {"prompt": str}。
    """
    new_state = compact_history_node(state)
    return {"prompt": new_state.prompt}


def make_generate_adapter(responder: Responder | None) -> GraphNode:
    """构造 generate 节点适配器（绑定 responder）。

    参数:
        responder: 可选生成函数；测试注入用，为空时走真实 Provider。

    返回:
        GraphNode: 标准 LangGraph 节点函数。
    """

    def adapter(state: AgentState) -> dict:
        """生成回答并返回 answer 字段更新。"""
        new_state = generate_node(state, responder=responder)
        return {"answer": new_state.answer}

    return adapter


def make_save_messages_adapter(
    repository: ConversationRepository | None,
) -> GraphNode:
    """构造 save_messages 节点适配器（绑定 repository）。

    参数:
        repository: 可选 PG Repository；为空时返回 memory:* 占位 id。

    返回:
        GraphNode: 标准 LangGraph 节点函数。
    """

    def adapter(state: AgentState) -> dict:
        """保存本轮消息并返回 message_ids 字段更新。"""
        new_state = save_messages_node(state, repository=repository)
        return {"message_ids": new_state.message_ids}

    return adapter
