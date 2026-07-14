"""大纲闸门常量（阶段 G · L0 策划闸门）。"""

# outline_phase 取值（AgentState / SSE 契约）
OUTLINE_PHASE_NONE = "none"
OUTLINE_PHASE_PROPOSED = "proposed"
OUTLINE_PHASE_APPROVED = "approved"

# 闸门拦截时返回给用户的固定提示（Chat content_delta）
OUTLINE_GATE_BLOCK_MESSAGE = (
    "请先在工作台下方完成「创作大纲」审阅并点击「确认并开始创作」。"
    "确认前我不会生成长篇正文或分镜脚本，以免偏离你的策划方向。"
)

# 豁免闸门的关键词（设定查询 / 局部改稿，与澄清层对齐）
OUTLINE_GATE_EXEMPT_KEYWORDS = ("师父", "设定", "查询", "检索", "润色", "改短", "是谁", "什么")
