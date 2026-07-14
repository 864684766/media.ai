"""ConfigResolver 辅助：L1 硬上限 clamp（数值安全阀）。

【clamp 是什么】
    把数字「卡」在允许范围内。类似音量旋钮有最大刻度，拧过头也会被限住。

【为什么需要】
    运维可能在 config.override.yaml 误写 max_retries: 999，
    若不 clamp，检索链可能无限重试拖垮服务。

【示例】
    输入 max_retries=99 → 输出 5（MAX_RETRIES_HARD_CAP）
    输入 retrieve_top_k=500 → 输出 100（RETRIEVE_TOP_K_HARD_CAP）
"""

from typing import Any

from app.core import config_constants as cc


def clamp_runtime_values(values: dict[str, Any]) -> dict[str, Any]:
    """将运行时数值限制在 L1 硬上限内。

    参数:
        values: 合并后的运行时参数字典。

    返回:
        dict[str, Any]: clamp 后的新字典。
    """
    clamped = dict(values)
    clamped[cc.FIELD_MAX_RETRIES] = _clamp_max_retries(values)
    clamped[cc.FIELD_RETRIEVE_TOP_K] = _clamp_top_k(
        values.get(cc.FIELD_RETRIEVE_TOP_K, cc.MIN_TOP_K),
        cc.RETRIEVE_TOP_K_HARD_CAP,
    )
    clamped[cc.FIELD_RERANK_TOP_K] = _clamp_top_k(
        values.get(cc.FIELD_RERANK_TOP_K, cc.MIN_TOP_K),
        cc.RERANK_TOP_K_HARD_CAP,
    )
    clamped[cc.FIELD_GRAPH_EXPAND_HOPS] = _clamp_graph_hops(values)
    return clamped


def _clamp_max_retries(values: dict[str, Any]) -> int:
    """限制 max_retries 在 [MIN_RETRIES, MAX_RETRIES_HARD_CAP]。

    参数:
        values: 含 max_retries 的字典。

    返回:
        int: clamp 后的重试次数。
    """
    raw = values.get(cc.FIELD_MAX_RETRIES, cc.MIN_RETRIES)
    numeric = int(raw)
    upper = cc.MAX_RETRIES_HARD_CAP
    return max(cc.MIN_RETRIES, min(numeric, upper))


def _clamp_top_k(raw_value: Any, hard_cap: int) -> int:
    """限制 top_k 类参数在 [MIN_TOP_K, hard_cap]。

    参数:
        raw_value: 原始值。
        hard_cap: L1 上限。

    返回:
        int: clamp 后的整数。
    """
    numeric = int(raw_value)
    return max(cc.MIN_TOP_K, min(numeric, hard_cap))


def _clamp_graph_hops(values: dict[str, Any]) -> int:
    """限制 graph_expand_hops 在合法区间。

    参数:
        values: 含 graph_expand_hops 的字典。

    返回:
        int: clamp 后的跳数。
    """
    raw = values.get(cc.FIELD_GRAPH_EXPAND_HOPS, cc.MIN_GRAPH_HOPS)
    numeric = int(raw)
    upper = cc.GRAPH_EXPAND_HOPS_HARD_CAP
    return max(cc.MIN_GRAPH_HOPS, min(numeric, upper))
