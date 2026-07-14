"""路由级联（Routing Cascade）配置常量。

【职责】
    集中维护 config/app.yaml route 段的键名、模式取值与默认值。
    与 docs/ARCHITECTURE.html sec-07 7.2「路由级联」对应。

【与 route_rule_constants.py 的分工】
    - route_rule_constants.py：规则层（L1）的内置关键词与置信度
    - 本文件：级联编排（模式选择、LLM 升级阈值）的配置键
"""

# ---- config/app.yaml route 段的键名 ----
YAML_KEY_ROUTE_SECTION = "route"
YAML_KEY_ROUTE_MODE = "mode"
YAML_KEY_LLM_CONFIDENCE_THRESHOLD = "llm_confidence_threshold"
YAML_KEY_KEYWORDS = "keywords"
YAML_KEY_KEYWORDS_WEB = "web"
YAML_KEY_KEYWORDS_CREATIVE = "creative"
YAML_KEY_KEYWORDS_PROJECT = "project"

# ---- mode 可选值 ----
ROUTE_MODE_RULES = "rules"      # 只用规则层
ROUTE_MODE_LLM = "llm"          # 每次都调 LLM 结构化路由
ROUTE_MODE_HYBRID = "hybrid"    # 级联：规则先判，置信度低才升级 LLM
VALID_ROUTE_MODES = (ROUTE_MODE_RULES, ROUTE_MODE_LLM, ROUTE_MODE_HYBRID)

# ---- 默认值 ----
DEFAULT_ROUTE_MODE = ROUTE_MODE_HYBRID
# 规则层置信度低于该值才调 LLM；规则命中为 0.6、未命中为 0.5（见 route_rule_constants）
# 默认 0.6：关键词命中（0.6）直接采用规则结果；未命中（0.5）升级 LLM——
# 即「明确的走快路径，模糊的问模型」，与业内级联做法一致
DEFAULT_LLM_CONFIDENCE_THRESHOLD = 0.6

# LLM 结构化路由成功时写入 RouteDecision.confidence 的值（高于规则层）
LLM_ROUTE_CONFIDENCE = 0.95

# LLM 路由的结果说明（写入 RouteDecision.reason，便于调试观察走了哪一层）
LLM_ROUTE_REASON = "LLM 结构化路由判定"
LLM_FALLBACK_REASON_SUFFIX = "（LLM 路由失败，已回退规则层）"
