"""route_question 规则层测试。

【覆盖点】
    1. 纯创作问题：仅 needs_creative。
    2. 查设定问题：needs_project 开启并产出 sub_queries。
    3. 时效问题：needs_web 开启。
    4. 复合问题（A+C）：project 与 creative 同时开启，domain=composite。
    5. 无关键词：默认创作通道，置信度较低。
"""

from app.graph.route_rule_constants import (
    DOMAIN_COMPOSITE,
    DOMAIN_GENERAL,
    DOMAIN_PROJECT,
)
from app.graph.route_rules import infer_route_decision


def test_pure_creative_question() -> None:
    """纯创作指令只应开启 needs_creative。"""
    decision = infer_route_decision("帮我续写一段打斗场面")
    assert decision.needs_creative is True
    assert decision.needs_project is False
    assert decision.needs_web is False


def test_project_question_enables_needs_project() -> None:
    """查人物关系应开启 needs_project 并给出检索子查询。"""
    decision = infer_route_decision("张三的师父是谁")
    assert decision.needs_project is True
    assert decision.sub_queries == ["张三的师父是谁"]
    assert decision.domain == DOMAIN_PROJECT


def test_chapter_reference_enables_needs_project() -> None:
    """「第三章」这类章节引用也应触发查库。"""
    decision = infer_route_decision("第三章结尾怎么描述的")
    assert decision.needs_project is True


def test_web_question_enables_needs_web() -> None:
    """时效类问题应开启 needs_web。"""
    decision = infer_route_decision("今天有什么新闻")
    assert decision.needs_web is True
    assert decision.needs_creative is False


def test_composite_question_marks_composite_domain() -> None:
    """创作 + 查设定的复合问题应为 composite。"""
    decision = infer_route_decision("续写打斗，并写明张三的师父是谁")
    assert decision.needs_project is True
    assert decision.needs_creative is True
    assert decision.domain == DOMAIN_COMPOSITE


def test_no_keyword_falls_back_to_creative() -> None:
    """无任何关键词时默认走创作通道（domain=general）。"""
    decision = infer_route_decision("你好呀")
    assert decision.needs_creative is True
    assert decision.domain == DOMAIN_GENERAL
    assert decision.confidence < 0.6
