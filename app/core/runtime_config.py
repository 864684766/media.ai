"""LangGraph 运行时配置模型（ConfigResolver 的最终输出类型）。

【本文件职责】
    用 Pydantic 定义「一次 Chat 请求里 Agent 该用哪些数字/开关」。
    LangGraph 每个节点通过 state.runtime_config 只读访问，避免到处传散参数。

【何时生成】
    请求入口调用 config_resolver.resolve() → 得到 RuntimeConfig 实例 → 写入 AgentState

【与 .env / app.yaml 的区别】
    .env        → AppSettings（端口、日志）
    app.yaml    → 原始 YAML 字典 + profile 选档
    RuntimeConfig → 已合并、已 clamp 的「Agent 专用」结构（本模型）

【示例】
    resolve({"profile": "dev"}) → RuntimeConfig(profile="dev", max_retries=2, ...)
"""

from pydantic import BaseModel, Field

from app.core import config_constants as cc


class RuntimeConfig(BaseModel):
    """单次 Chat 请求在图内使用的运行时参数（字段均有中文说明）。

    每个 Field 的 description 可在 IDE 悬停时看到，便于初学者对照。
    """

    profile: str = Field(
        default=cc.DEFAULT_PROFILE,
        description="当前套餐名：dev | prod | strict，来自 app.yaml 的 profile 键",
    )
    max_retries: int = Field(
        default=2,
        ge=cc.MIN_RETRIES,
        description="检索或生成失败时最多重试次数；被 L1 上限 5 限制",
    )
    retrieve_top_k: int = Field(
        default=30,
        ge=cc.MIN_TOP_K,
        description="Hybrid 检索一路最多召回多少 chunk；dev=30 prod=50",
    )
    rerank_top_k: int = Field(
        default=5,
        ge=cc.MIN_TOP_K,
        description="Rerank 后保留几条给模型；strict 档默认 3",
    )
    graph_expand_hops: int = Field(
        default=2,
        ge=cc.MIN_GRAPH_HOPS,
        description="Neo4j 图扩展跳数；Phase 2 检索链使用",
    )
    web_search: str = Field(
        default=cc.WEB_SEARCH_CONDITIONAL,
        description="Web 策略；第一版固定 conditional=按路由开关决定是否联网",
    )
    refuse_when_no_evidence: bool = Field(
        default=False,
        description="Grader 无证据时是否拒答；strict 档为 true",
    )
