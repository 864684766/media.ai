"""历史摘要器工厂。"""

from app.graph.history_summarizer import HistorySummarizer, TruncationSummarizer
from app.retrieval.chat_provider_factory import build_chat_provider


def build_history_summarizer(yaml_config: dict | None = None) -> HistorySummarizer | TruncationSummarizer:
    """构建摘要器；Provider 不可用时用截断实现。"""
    try:
        provider = build_chat_provider(yaml_config)
        return HistorySummarizer(provider)
    except Exception:  # noqa: BLE001
        return TruncationSummarizer()
