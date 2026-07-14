"""Web 搜索（Tavily 适配器）。

【职责】
    needs_web=true 或 Grader no_evidence 兜底时联网搜索，
    返回 WebResult 列表注入 generate。
    对应 docs/ARCHITECTURE.html sec-07 路线 B 与 config/app.yaml web_search 段。

【密钥与降级】
    API Key 从 .env 的 TAVILY_API_KEY 读取（不进 Git）；
    未配置 Key 时返回空列表并不报错——保证无 Key 环境下主流程可用。

【测试】
    构造时可注入 httpx transport（MockTransport），不真实联网。
"""

import os

import httpx

from app.retrieval import retrieval_constants as rc
from app.retrieval.retrieval_models import WebResult


class TavilyWebSearcher:
    """Tavily 搜索客户端。

    参数说明:
        api_key: Tavily API Key；None 时从环境变量读取。
        max_results: 最多返回条数（来自 config/app.yaml web_search.max_results）。
        transport: 可选 httpx transport，测试注入 MockTransport 用。
    """

    def __init__(
        self,
        api_key: str | None = None,
        max_results: int = 5,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """初始化搜索客户端。"""
        self._api_key = api_key if api_key is not None else os.getenv(rc.TAVILY_API_KEY_ENV)
        self._max_results = max_results
        self._transport = transport

    @property
    def is_configured(self) -> bool:
        """返回是否已配置 API Key。"""
        return bool(self._api_key)

    def search(self, query: str) -> list[WebResult]:
        """执行联网搜索。

        参数:
            query: 查询文本。

        返回:
            list[WebResult]: 搜索结果；未配置 Key 时为空列表。
        """
        if not self.is_configured:
            return []
        payload = self._build_payload(query)
        data = self._post(payload)
        return _parse_results(data)

    def _build_payload(self, query: str) -> dict:
        """组装 Tavily 请求体。"""
        return {
            rc.TAVILY_FIELD_API_KEY: self._api_key,
            rc.TAVILY_FIELD_QUERY: query,
            rc.TAVILY_FIELD_MAX_RESULTS: self._max_results,
        }

    def _post(self, payload: dict) -> dict:
        """发送 HTTP 请求并返回 JSON。"""
        with httpx.Client(
            transport=self._transport,
            timeout=rc.WEB_SEARCH_TIMEOUT_SECONDS,
        ) as client:
            response = client.post(rc.TAVILY_API_URL, json=payload)
            response.raise_for_status()
            return response.json()


def _parse_results(data: dict) -> list[WebResult]:
    """把 Tavily 响应解析为 WebResult 列表。

    参数:
        data: Tavily API 返回 JSON。

    返回:
        list[WebResult]: 解析结果；results 字段缺失时为空列表。
    """
    raw_results = data.get(rc.TAVILY_FIELD_RESULTS, [])
    if not isinstance(raw_results, list):
        return []
    return [
        WebResult(
            title=str(item.get(rc.TAVILY_FIELD_TITLE, "")),
            url=str(item.get(rc.TAVILY_FIELD_URL, "")),
            snippet=str(item.get(rc.TAVILY_FIELD_CONTENT, "")),
        )
        for item in raw_results
        if isinstance(item, dict)
    ]
