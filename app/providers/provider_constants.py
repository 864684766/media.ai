"""Provider Registry 常量。

【职责】
    集中维护 provider id、OpenAI 兼容接口路径、默认超时等字面量。

【为什么单独放】
    后续新增厂商时优先改常量/注册表，避免在业务代码里散落 "zhipu"、"/chat/completions"。
"""

# OpenAI Chat Completions 兼容接口路径
OPENAI_CHAT_COMPLETIONS_PATH = "/chat/completions"

# Provider id：配置里的 model.provider 必须匹配这些 id
PROVIDER_ID_ZHIPU = "zhipu"
PROVIDER_ID_DEEPSEEK = "deepseek"
PROVIDER_ID_KIMI = "kimi"
PROVIDER_ID_LOCAL_OPENAI = "local-openai-compatible"

# 默认 API Base；用户可在 config/app.yaml 覆盖
DEFAULT_ZHIPU_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEFAULT_KIMI_API_BASE = "https://api.moonshot.cn/v1"
DEFAULT_LOCAL_OPENAI_API_BASE = "http://127.0.0.1:8001/v1"

# HTTP 参数
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 60.0
AUTHORIZATION_HEADER_NAME = "Authorization"
CONTENT_TYPE_HEADER_NAME = "Content-Type"
JSON_CONTENT_TYPE = "application/json"
BEARER_TOKEN_PREFIX = "Bearer"

# 健康检查提示词：尽量短，避免真实检查时浪费 token
PROVIDER_HEALTH_CHECK_PROMPT = "请只回复 OK"

# app.yaml 中的键名
YAML_KEY_MODEL_SECTION = "model"
YAML_KEY_PROVIDER = "provider"
YAML_KEY_MODEL = "model"
YAML_KEY_API_BASE = "api_base"

# OpenAI Chat Completions 协议键名（请求体；外部协议契约，一处权威）
OPENAI_FIELD_MODEL = "model"
OPENAI_FIELD_MESSAGES = "messages"
OPENAI_FIELD_TEMPERATURE = "temperature"
OPENAI_FIELD_STREAM = "stream"

# OpenAI Chat Completions 协议键名（响应体与 SSE 流解析）
OPENAI_FIELD_CHOICES = "choices"
OPENAI_FIELD_MESSAGE = "message"
OPENAI_FIELD_CONTENT = "content"
OPENAI_FIELD_DELTA = "delta"
OPENAI_FIELD_USAGE = "usage"

# OpenAI SSE 流的行前缀与结束标记
OPENAI_SSE_DATA_PREFIX = "data: "
OPENAI_SSE_DONE_MARKER = "[DONE]"
