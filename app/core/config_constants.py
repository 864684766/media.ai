"""配置体系常量（L1 硬上限与 Profile 相关字面量）。

【本文件职责】
    集中存放配置相关的「名字」和「安全边界数值」，避免在多个 .py 里写死字符串。

【三层配置对应关系】（详见 ARCHITECTURE sec-08）
    L1  本文件中的 MAX_*_HARD_CAP  → 代码写死，运维改 config 也绕不过
    L2  profile_presets.py         → dev/prod/strict 三套默认数
    L3  config/config.override.yaml → 可选，高级覆盖（默认不存在）

【示例】
    运维在 override 写 max_retries: 99 → ConfigResolver 最后 clamp 成 5（MAX_RETRIES_HARD_CAP）
"""

# =============================================================================
# Profile 名称（L2 选档）— 与 config/app.yaml 的 profile: dev 对应
# =============================================================================
PROFILE_DEV = "dev"
PROFILE_PROD = "prod"
PROFILE_STRICT = "strict"
# 当 app.yaml 没写 profile 或写了非法值时，回退到 dev
DEFAULT_PROFILE = PROFILE_DEV

# app.yaml 里选档用的键名，例如: profile: strict
YAML_KEY_PROFILE = "profile"

# =============================================================================
# L1 硬上限 — 「clamp」会把超过上限的数压到上限以内
# =============================================================================
# 检索/生成最多重试几次；例：override 写 99 → 实际最多 5
MAX_RETRIES_HARD_CAP = 5
MIN_RETRIES = 1
# Grader 评分阈值（Phase 2）；低于 0.7 可能判为无证据
GRADER_THRESHOLD = 0.7
# Hybrid 一路最多召回多少 chunk；例：写 500 → 压到 100
RETRIEVE_TOP_K_HARD_CAP = 100
# Rerank 后最多保留几条；例：写 50 → 压到 20
RERANK_TOP_K_HARD_CAP = 20
# Neo4j 图扩展最多几跳；例：写 10 → 压到 4
GRAPH_EXPAND_HOPS_HARD_CAP = 4
MIN_TOP_K = 1
MIN_GRAPH_HOPS = 0

# Web 何时启用：conditional = 仅 route 判定 needs_web 或 Grader 兜底时
WEB_SEARCH_CONDITIONAL = "conditional"

# =============================================================================
# RuntimeConfig 字段名 — 与 profile 映射表、Pydantic 模型字段一致
# =============================================================================
FIELD_MAX_RETRIES = "max_retries"
FIELD_RETRIEVE_TOP_K = "retrieve_top_k"
FIELD_RERANK_TOP_K = "rerank_top_k"
FIELD_GRAPH_EXPAND_HOPS = "graph_expand_hops"
FIELD_WEB_SEARCH = "web_search"
FIELD_REFUSE_WHEN_NO_EVIDENCE = "refuse_when_no_evidence"
FIELD_PROFILE = "profile"

# 需要做「数值 clamp」的字段列表（字符串/布尔字段不在此列）
# 用途：文档化 + 将来可循环 clamp；当前实现在 config_resolver_clamp.py 逐字段处理
# 例：max_retries、retrieve_top_k 是整数；web_search 是字符串故不在此元组
RUNTIME_NUMERIC_FIELDS = (
    FIELD_MAX_RETRIES,
    FIELD_RETRIEVE_TOP_K,
    FIELD_RERANK_TOP_K,
    FIELD_GRAPH_EXPAND_HOPS,
)
