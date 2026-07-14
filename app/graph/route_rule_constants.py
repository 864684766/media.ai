"""route_question 规则层关键词常量。

【职责】
    集中维护路由规则层使用的中文关键词表与默认值。
    与 docs/ARCHITECTURE.html sec-07.2「规则层」对应。

【如何扩展】
    新增触发词只需往对应元组里追加，不用改判定逻辑（app/graph/route_rules.py）；
    运维也可在 config/app.yaml route.keywords 覆盖，本文件仅为内置默认。
"""

from app.core import constants as core_constants

# 触发 needs_web 的时效/库外关键词：出现即认为需要联网查询
WEB_KEYWORDS: tuple[str, ...] = (
    "今天",
    "今日",
    "最新",
    "新闻",
    "实时",
    "热点",
    "天气",
    "股价",
    "联网",
    "搜索一下",
)

# 触发 needs_creative 的创作/润色/改稿关键词
CREATIVE_KEYWORDS: tuple[str, ...] = (
    "续写",
    "写一",
    "帮我写",
    "润色",
    "改写",
    "改短",
    "改长",
    "扩写",
    "重写",
    "创作",
    "起个",
    "取名",
    "大纲",
    "分镜",
    "脚本",
)

# 触发 needs_project 的作品库/设定查询关键词
PROJECT_KEYWORDS: tuple[str, ...] = (
    "设定",
    "原文",
    "书里",
    "作品里",
    "之前写的",
    "上一章",
    "是谁",
    "人物关系",
    "世界观",
)

# 匹配「第 X 章」类章节引用的正则（X 可为中文或阿拉伯数字）
CHAPTER_PATTERN: str = r"第[一二三四五六七八九十百千0-9]+章"

# 规则层命中时的置信度（低于 LLM 结构化路由，提示这是启发式结果）
RULE_CONFIDENCE: float = 0.6

# 没有任何关键词命中时的置信度（默认走创作通道）
DEFAULT_CONFIDENCE: float = 0.5

# reason 说明文案（写入 RouteDecision.reason，标明决策来自哪一层）
REASON_RULE_MATCHED = "规则层关键词判定"
REASON_NO_KEYWORD = "无关键词命中，默认创作通道"

# domain 取值：权威定义在 app/core/constants.py（sec-15 跨层契约），
# 此处保留 graph 层别名引用，避免调用方大面积改动
DOMAIN_GENERAL = core_constants.ROUTE_DOMAIN_GENERAL
DOMAIN_PROJECT = core_constants.ROUTE_DOMAIN_PROJECT
DOMAIN_REALTIME = core_constants.ROUTE_DOMAIN_REALTIME
DOMAIN_COMPOSITE = core_constants.ROUTE_DOMAIN_COMPOSITE
