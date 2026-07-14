"""创作澄清（Clarification）层内常量。

【职责】
    clarification_sessions 状态、选题模式等 API 与 ORM 共用字面量。

【何时调用】
    澄清服务、模板构建、测试断言。
"""

# session 状态
CLARIFICATION_STATUS_COLLECTING = "collecting"
CLARIFICATION_STATUS_COMPLETED = "completed"
CLARIFICATION_STATUS_SKIPPED = "skipped"

# 单题选择模式（首版仅 single）
SELECTION_MODE_SINGLE = "single"

# 创作类型（与 ChatRequest.creation_type 对齐）
CREATION_TYPE_NOVEL = "novel"
CREATION_TYPE_VIDEO = "video"

# 默认配置
DEFAULT_CLARIFICATION_MAX_ROUNDS = 3
DEFAULT_QUESTIONS_PER_ROUND_MAX = 5
DEFAULT_MIN_BRIEF_CHARS = 20
