"""Grader 模块常量。

【职责】
    集中管理 Grader 模式、LLM 提示与解析键名。
"""

# app.yaml grader 段键名
YAML_KEY_GRADER_SECTION = "grader"
YAML_KEY_GRADER_MODE = "mode"

# Grader 模式：rule 仅规则；llm 仅 LLM；hybrid 规则优先、不确定时问 LLM
GRADER_MODE_RULE = "rule"
GRADER_MODE_LLM = "llm"
GRADER_MODE_HYBRID = "hybrid"
DEFAULT_GRADER_MODE = GRADER_MODE_HYBRID

# LLM Grader 采样温度（判定任务宜低温）
LLM_GRADER_TEMPERATURE = 0.0

# LLM 输出 JSON 字段
GRADER_FIELD_VERDICT = "verdict"

# 规则版：有 chunk 但重叠弱于 relevant 阈值、又非零 → irrelevant
GRADER_IRRELEVANT_MIN_SCORE = 0.1
