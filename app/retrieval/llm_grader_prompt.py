"""LLM Grader 提示词构造。"""

from app.retrieval.retrieval_constants import (
    VERDICT_IRRELEVANT,
    VERDICT_NO_EVIDENCE,
    VERDICT_RELEVANT,
)


def build_grader_messages(question: str, chunk_texts: list[str]) -> list[dict[str, str]]:
    """构造 Grader 对话消息。

    参数:
        question: 用户问题。
        chunk_texts: 候选证据文本（截断后）。

    返回:
        list[dict]: OpenAI 兼容 messages。
    """
    evidence = "\n".join(f"- {text[:200]}" for text in chunk_texts[:5])
    system = (
        "你是检索相关性评估器。只输出 JSON："
        f'{{"verdict":"{VERDICT_RELEVANT}|{VERDICT_IRRELEVANT}|{VERDICT_NO_EVIDENCE}"}}'
    )
    user = f"问题：{question}\n证据：\n{evidence}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
