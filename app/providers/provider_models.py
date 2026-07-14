"""Provider 数据模型。

【职责】
    定义 LLM 调用前后的结构，避免代码里直接传散乱 dict。

【调用位置】
    OpenAICompatibleProvider.chat() 接收 ChatCompletionRequest，返回 ChatCompletionResult。

【示例】
    ChatCompletionRequest(messages=[ChatMessage(role="user", content="你好")])
    → ChatCompletionResult(content="你好，我是...")
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """单条对话消息。

    参数说明:
        role: 消息角色，常见为 system / user / assistant。
        content: 消息正文。
    """

    role: str = Field(description="消息角色：system / user / assistant")
    content: str = Field(description="消息正文")


class ModelConfig(BaseModel):
    """当前选中的模型配置（来自 config/app.yaml + .env）。

    参数说明:
        provider: Provider id，如 zhipu。
        model: 具体模型名，如 glm-4-flash。
        api_base: OpenAI 兼容 API 根地址。
        api_key: API Key；来自 .env，不写入 app.yaml。
    """

    provider: str = Field(description="Provider id")
    model: str = Field(description="模型名称")
    api_base: str = Field(description="OpenAI 兼容 API 根地址")
    api_key: str | None = Field(default=None, description="API Key")


class ChatCompletionRequest(BaseModel):
    """一次 Chat Completions 请求。

    参数说明:
        messages: 按顺序传给模型的消息。
        temperature: 采样温度，越高越发散。
        stream: 是否流式；当前骨架先支持非流式测试。
    """

    messages: list[ChatMessage]
    temperature: float = Field(default=0.7)
    stream: bool = Field(default=False)


class ChatCompletionResult(BaseModel):
    """模型返回的简化结果。

    参数说明:
        content: assistant 回复正文。
        raw: 原始 JSON，便于调试和后续取 usage。
    """

    content: str
    raw: dict


class ProviderHealthResult(BaseModel):
    """Provider 连通性检查结果。

    参数说明:
        provider: Provider id，如 zhipu。
        model: 模型名称。
        configured: 是否已配置 API Key。
        reachable: 是否成功获得模型响应。
        message: 中文说明；不包含 API Key。
    """

    provider: str = Field(description="Provider id")
    model: str = Field(description="模型名称")
    configured: bool = Field(description="是否已配置 API Key")
    reachable: bool = Field(description="是否成功调用")
    message: str = Field(default="", description="状态说明")
