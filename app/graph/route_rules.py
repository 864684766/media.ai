"""route_question 规则层判定逻辑。

【职责】
    根据用户问题中的关键词，推断三个能力开关：
    needs_project（查作品库）/ needs_web（联网）/ needs_creative（创作）。
    这是 docs/ARCHITECTURE.html sec-07.2「路由级联」的 L1 层（快路径）；
    置信度低时由 app/graph/route_cascade.py 升级到 L3 LLM 结构化路由。

【关键词从哪来】
    不再硬编码使用常量：由调用方传入 RouteKeywords
    （config/app.yaml route.keywords 可覆盖，默认取 route_rule_constants.py 内置表）。

【何时被调用】
    app/graph/route_cascade.py 级联编排内调用 infer_route_decision()。

【简例】
    infer_route_decision("续写打斗，张三的师父是谁？")
    -> RouteDecision(needs_project=True, needs_creative=True, domain="composite")
"""

import re

from app.graph.route_domain_helper import resolve_domain
from app.graph.route_rule_constants import (
    CHAPTER_PATTERN,
    DEFAULT_CONFIDENCE,
    REASON_NO_KEYWORD,
    REASON_RULE_MATCHED,
    RULE_CONFIDENCE,
)
from app.graph.route_settings_reader import RouteKeywords
from app.schemas.agent_state import RouteDecision


def _contains_any(question: str, keywords: tuple[str, ...]) -> bool:
    """判断问题是否命中关键词表中的任意一个词。

    参数:
        question: 用户问题原文。
        keywords: 关键词表。

    返回:
        bool: 命中任意关键词返回 True。
    """
    return any(keyword in question for keyword in keywords)


def _detect_project_need(question: str, project_keywords: tuple[str, ...]) -> bool:
    """判断是否需要查作品库（关键词或「第 X 章」引用）。

    参数:
        question: 用户问题原文。
        project_keywords: 作品库关键词表（可来自 app.yaml 覆盖）。

    返回:
        bool: 需要查库返回 True。
    """
    if _contains_any(question, project_keywords):
        return True
    return re.search(CHAPTER_PATTERN, question) is not None


def infer_route_decision(
    question: str,
    keywords: RouteKeywords | None = None,
) -> RouteDecision:
    """规则层路由：从问题文本推断能力开关。

    参数:
        question: 用户问题原文。
        keywords: 关键词表；None 时使用内置默认（RouteKeywords 默认值）。

    返回:
        RouteDecision: 含 needs_* 开关、domain、sub_queries 的决策结果。
    """
    words = keywords if keywords is not None else RouteKeywords()
    needs_project = _detect_project_need(question, words.project)
    needs_web = _contains_any(question, words.web)
    has_creative_word = _contains_any(question, words.creative)
    # 创作开关：命中创作词，或没有任何查询类开关时默认走创作（几乎每轮 true）
    needs_creative = has_creative_word or not (needs_project or needs_web)
    matched_any = needs_project or needs_web or has_creative_word
    return RouteDecision(
        domain=resolve_domain(needs_project, needs_web, needs_creative),
        needs_project=needs_project,
        needs_web=needs_web,
        needs_creative=needs_creative,
        # 规则层暂不做意图拆分：整句作为唯一检索子查询
        sub_queries=[question] if needs_project else [],
        confidence=RULE_CONFIDENCE if matched_any else DEFAULT_CONFIDENCE,
        reason=REASON_RULE_MATCHED if matched_any else REASON_NO_KEYWORD,
    )
