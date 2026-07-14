"""检索流水线常量。

【职责】
    集中管理 RRF 参数、Grader 判定阈值、Web 搜索端点等字面量。
"""

# RRF（Reciprocal Rank Fusion）平滑常数：score = 1 / (k + rank)
# 60 是信息检索论文与各引擎的通用默认值
RRF_K = 60

# Grader 判定结果枚举（与 sec-15 GradeResult 契约一致）
VERDICT_RELEVANT = "relevant"
VERDICT_IRRELEVANT = "irrelevant"
VERDICT_NO_EVIDENCE = "no_evidence"

# 规则版 Grader：重叠覆盖率 >= 该值视为 relevant；有部分命中但不足为 irrelevant
GRADER_MIN_COVERAGE_RATIO = 0.35
GRADER_MIN_OVERLAP_SCORE = 1.0

# Tavily Web 搜索 API 端点与密钥环境变量名
TAVILY_API_URL = "https://api.tavily.com/search"
TAVILY_API_KEY_ENV = "TAVILY_API_KEY"

# Tavily 请求体键名（外部 API 契约，见 https://docs.tavily.com）
TAVILY_FIELD_API_KEY = "api_key"
TAVILY_FIELD_QUERY = "query"
TAVILY_FIELD_MAX_RESULTS = "max_results"

# Tavily 响应体键名（解析用；content 字段即摘要文本）
TAVILY_FIELD_RESULTS = "results"
TAVILY_FIELD_TITLE = "title"
TAVILY_FIELD_URL = "url"
TAVILY_FIELD_CONTENT = "content"

# Web 搜索请求超时秒数
WEB_SEARCH_TIMEOUT_SECONDS = 10.0

# citation 摘要最长字符数（SSE citation 事件的 excerpt 字段）
CITATION_EXCERPT_MAX_CHARS = 80
