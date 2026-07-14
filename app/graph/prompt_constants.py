"""Prompt 拼装段落常量。

【职责】
    集中维护 prompt_builder.py 拼装 prompt 时使用的段落标题字面量。
    这些标题是「代码与模型之间的约定」：模型按段落理解上下文，
    测试也按标题断言拼装结果——必须一处权威、多处引用。

【何时被调用】
    - app/graph/prompt_builder.py 拼装 state.prompt
    - tests/ 中对 prompt 内容的断言
"""

# 各段落标题（拼装顺序：系统人设 → 历史消息 → 作品库证据 → 联网结果 → 本轮用户）
PROMPT_SECTION_SYSTEM = "【系统人设】"
PROMPT_SECTION_HISTORY = "【历史消息】"
PROMPT_SECTION_HISTORY_SUMMARY = "【历史摘要】"
PROMPT_SECTION_EVIDENCE = "【作品库证据】"
PROMPT_SECTION_WEB = "【联网结果】"
PROMPT_SECTION_QUESTION = "【本轮用户】"
PROMPT_SECTION_APPROVED_OUTLINE = "【已确认大纲】"

# 证据段的引导语：提示模型基于证据回答（放标题后同一行）
PROMPT_EVIDENCE_GUIDE = "（回答请基于以下内容）"

# 段落之间的分隔符
PROMPT_PART_SEPARATOR = "\n\n"
