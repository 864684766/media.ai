"""LLM Grader 响应解析。"""

import json
import re

from app.retrieval import grader_constants as gc
from app.retrieval.retrieval_constants import (
    VERDICT_IRRELEVANT,
    VERDICT_NO_EVIDENCE,
    VERDICT_RELEVANT,
)


def parse_grader_response(content: str) -> str | None:
    """从模型输出解析 verdict。

    参数:
        content: 模型原文。

    返回:
        str | None: relevant / irrelevant / no_evidence；失败返回 None。
    """
    payload = _extract_json(content)
    if payload is None:
        return None
    verdict = str(payload.get(gc.GRADER_FIELD_VERDICT, "")).strip()
    if verdict in (VERDICT_RELEVANT, VERDICT_IRRELEVANT, VERDICT_NO_EVIDENCE):
        return verdict
    return None


def _extract_json(content: str) -> dict | None:
    """从文本中提取 JSON 对象。"""
    match = re.search(r"\{[^{}]*\}", content, re.DOTALL)
    if match is None:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
