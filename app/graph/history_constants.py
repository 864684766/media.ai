"""历史压缩常量。"""

# 超过该估算 token 数触发压缩（字符数近似）
HISTORY_TOKEN_THRESHOLD = 2000

# 压缩后保留的最近消息条数
HISTORY_KEEP_RECENT_COUNT = 6

# LLM 摘要温度
HISTORY_SUMMARY_TEMPERATURE = 0.3
