"""Query Rewrite 提示词。"""


def build_rewrite_messages(question: str, query: str) -> list[dict[str, str]]:
    """构造改写子查询的 messages。

    参数:
        question: 用户原问题。
        query: 当前检索 query。

    返回:
        list[dict]: OpenAI 兼容 messages。
    """
    system = "你是检索 query 改写器。只输出一行改写后的检索词，不要解释。"
    user = f"原问题：{question}\n当前 query：{query}\n请改写为更利于作品库检索的 query："
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
