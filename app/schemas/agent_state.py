"""LangGraph AgentState 数据契约。

【职责】
    定义图内共享 state 的字段。节点只读/写自己负责的字段，减少隐式副作用。

【当前阶段】
    先用于最小顺序执行器；后续接 LangGraph StateGraph 时继续复用。
"""

from pydantic import BaseModel, Field

from app.core.constants import ROUTE_DOMAIN_GENERAL, ROUTE_REASON_DEFAULT
from app.core.runtime_config import RuntimeConfig
from app.retrieval.retrieval_models import RetrievalContext
from app.skills.skill_models import SkillContext


class ChatHistoryMessage(BaseModel):
    """历史消息结构。

    参数说明:
        role: user / assistant / system。
        content: 消息正文。
    """

    role: str = Field(description="消息角色")
    content: str = Field(description="消息正文")


class RouteDecision(BaseModel):
    """路由决策结果（由路由级联写入，见 sec-07 7.2）。"""

    domain: str = Field(default=ROUTE_DOMAIN_GENERAL, description="兼容字段")
    needs_project: bool = Field(default=False, description="是否查作品库")
    needs_web: bool = Field(default=False, description="是否联网")
    needs_creative: bool = Field(default=True, description="是否需要创作/对话")
    sub_queries: list[str] = Field(default_factory=list, description="检索子查询")
    confidence: float = Field(default=1.0, description="路由置信度")
    reason: str = Field(default=ROUTE_REASON_DEFAULT, description="原因说明（标明来自哪一层）")


class AgentState(BaseModel):
    """单次 Chat 在图内流转的共享状态。

    字段说明与 docs/ARCHITECTURE.html sec-15 对齐。
    """

    question: str = Field(description="用户原始问题")
    conversation_id: str = Field(description="业务会话 id")
    thread_id: str = Field(description="图 checkpoint id，默认等于 conversation_id")
    project_id: str | None = Field(default=None, description="项目 id")
    requested_skill_id: str | None = Field(
        default=None,
        description="请求显式指定的 Skill id；LangGraph 节点从 state 读取（节点签名只能收 state）",
    )
    creation_type: str | None = Field(
        default=None,
        description="创作类型 novel / video；load_skill 据此过滤 Skill 池",
    )
    runtime_config: RuntimeConfig = Field(description="运行时配置")
    skill: SkillContext | None = Field(default=None, description="当前 Skill")
    history: list[ChatHistoryMessage] = Field(default_factory=list)
    history_summary: str = Field(default="", description="历史压缩摘要")
    route: RouteDecision | None = Field(default=None, description="路由决策")
    retrieval: RetrievalContext | None = Field(
        default=None,
        description="检索/Web 证据集合；needs_project 或 needs_web 时由 retrieve_context 节点写入",
    )
    prompt: str = Field(default="", description="拼装后的 prompt 骨架")
    answer: str = Field(default="", description="assistant 回复")
    message_ids: list[str] = Field(default_factory=list, description="持久化消息 id")
    creative_plan_id: str | None = Field(default=None, description="已确认大纲 plan_id（阶段 G）")
    approved_outline_md: str | None = Field(default=None, description="已确认大纲 Markdown 镜像")
    outline_phase: str | None = Field(
        default=None,
        description="大纲闸门阶段 none / proposed / approved",
    )
