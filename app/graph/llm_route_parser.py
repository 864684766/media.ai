"""LLM 路由输出解析器。

【职责】
    把模型返回的文本解析成 RouteDecision；解析失败返回 None
    （由级联编排回退规则层结果，路由永不因模型输出格式崩溃）。

【容错点】
    - 模型可能包一层 ```json 代码块 → 先剥壳
    - 模型可能在 JSON 前后加说明文字 → 截取首个 { 到末个 }
    - 字段缺失/类型不对 → 按 RouteDecision 默认值兜底

【简例】
    parse_route_response('{"needs_project": true, ...}') -> RouteDecision(...)
    parse_route_response('抱歉我不明白') -> None
"""

import json

from app.graph import route_cascade_constants as rc
from app.graph.route_domain_helper import resolve_domain
from app.schemas.agent_state import RouteDecision

# JSON 输出中的字段名（与 llm_route_prompt.py 的提示词约定一致）
FIELD_NEEDS_PROJECT = "needs_project"
FIELD_NEEDS_WEB = "needs_web"
FIELD_NEEDS_CREATIVE = "needs_creative"
FIELD_SUB_QUERIES = "sub_queries"
FIELD_REASON = "reason"


def parse_route_response(content: str) -> RouteDecision | None:
    """解析 LLM 返回文本为 RouteDecision。

    参数:
        content: 模型返回的原始文本。

    返回:
        RouteDecision | None: 解析成功返回决策；失败返回 None。
    """
    data = _extract_json_object(content)
    if data is None:
        return None
    needs_project = _read_bool(data, FIELD_NEEDS_PROJECT)
    needs_web = _read_bool(data, FIELD_NEEDS_WEB)
    needs_creative = _read_bool(data, FIELD_NEEDS_CREATIVE)
    return RouteDecision(
        domain=resolve_domain(needs_project, needs_web, needs_creative),
        needs_project=needs_project,
        needs_web=needs_web,
        needs_creative=needs_creative,
        sub_queries=_read_sub_queries(data),
        confidence=rc.LLM_ROUTE_CONFIDENCE,
        reason=_read_reason(data),
    )


def _extract_json_object(content: str) -> dict | None:
    """从文本中截取并解析首个 JSON 对象；失败返回 None。"""
    start = content.find("{")
    end = content.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _read_bool(data: dict, key: str) -> bool:
    """读取布尔字段；缺失或类型不对按 False 处理。"""
    raw = data.get(key)
    return raw if isinstance(raw, bool) else False


def _read_sub_queries(data: dict) -> list[str]:
    """读取检索子查询数组；过滤非字符串项。"""
    raw = data.get(FIELD_SUB_QUERIES)
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, str) and item]


def _read_reason(data: dict) -> str:
    """读取判定说明；缺失时用统一标识。"""
    raw = data.get(FIELD_REASON)
    return raw if isinstance(raw, str) and raw else rc.LLM_ROUTE_REASON
