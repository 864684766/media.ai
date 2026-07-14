"""语义路由常量。

【职责】
    各意图类别的示例句（utterances）与相似度阈值。
    L2 语义路由：问题 embedding 与示例句余弦相似度最高者即为意图。
"""

# 意图类别名（与 RouteDecision 能力开关联动）
INTENT_PROJECT = "project"
INTENT_WEB = "web"
INTENT_CREATIVE = "creative"

# 相似度低于该值视为未命中（升级到 L3 LLM）
DEFAULT_SEMANTIC_THRESHOLD = 0.55

# 语义路由命中时的置信度（介于规则 0.6 与 LLM 0.95 之间）
SEMANTIC_ROUTE_CONFIDENCE = 0.75
SEMANTIC_ROUTE_REASON = "语义路由示例句匹配"

# 各类意图示例句（可扩展至 config/app.yaml route.semantic_utterances）
PROJECT_UTTERANCES: tuple[str, ...] = (
    "张三的师父是谁",
    "查一下主角设定",
    "世界观是怎样的",
    "第三章写了什么",
)

WEB_UTTERANCES: tuple[str, ...] = (
    "今天有什么新闻",
    "查一下最新票房",
    "联网搜索一下",
    "实时天气怎么样",
)

CREATIVE_UTTERANCES: tuple[str, ...] = (
    "帮我续写一段",
    "润色这段文字",
    "写一个大纲",
    "改短一点",
)
