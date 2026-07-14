"""历史摘要提示词。"""

from app.schemas.agent_state import ChatHistoryMessage


def build_summary_messages(messages: list[ChatHistoryMessage]) -> list[dict[str, str]]:
    """构造历史压缩摘要 messages。"""
    lines = [f"{item.role}: {item.content}" for item in messages]
    system = "你是会话摘要器。用中文输出 3~5 句摘要，保留人物、情节与未决问题。"
    user = "请摘要以下对话：\n" + "\n".join(lines)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
