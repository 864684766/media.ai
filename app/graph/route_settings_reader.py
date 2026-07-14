"""路由配置读取器。

【职责】
    从 config/app.yaml 的 route 段读取级联模式、LLM 升级阈值
    与可选的关键词覆盖表；非法值一律回退默认，保证路由永不因配置崩溃。

【何时被调用】
    - app/graph/route_cascade.py：决定走哪一层
    - app/graph/route_classifier_factory.py：决定是否构建 LLM 分类器

【简例】
    load_route_settings() -> RouteSettings(mode="hybrid", llm_confidence_threshold=0.9)
"""

from typing import Any

from pydantic import BaseModel, Field

from app.core.config_yaml_loader import load_app_yaml
from app.graph import route_cascade_constants as rc
from app.graph import route_rule_constants as rrc


class RouteKeywords(BaseModel):
    """规则层三组关键词表（可被 app.yaml 覆盖）。

    参数说明:
        web: 触发 needs_web 的关键词。
        creative: 触发 needs_creative 的关键词。
        project: 触发 needs_project 的关键词。
    """

    web: tuple[str, ...] = Field(default=rrc.WEB_KEYWORDS, description="联网关键词")
    creative: tuple[str, ...] = Field(default=rrc.CREATIVE_KEYWORDS, description="创作关键词")
    project: tuple[str, ...] = Field(default=rrc.PROJECT_KEYWORDS, description="作品库关键词")


class RouteSettings(BaseModel):
    """route 段配置结果。

    参数说明:
        mode: rules / llm / hybrid（级联，默认）。
        llm_confidence_threshold: hybrid 模式下规则置信度低于该值才调 LLM。
        keywords: 规则层关键词表（含 yaml 覆盖后的结果）。
    """

    mode: str = Field(default=rc.DEFAULT_ROUTE_MODE, description="路由模式")
    llm_confidence_threshold: float = Field(
        default=rc.DEFAULT_LLM_CONFIDENCE_THRESHOLD,
        description="LLM 升级阈值",
    )
    keywords: RouteKeywords = Field(default_factory=RouteKeywords, description="关键词表")


def load_route_settings(yaml_config: dict[str, Any] | None = None) -> RouteSettings:
    """读取 route 段配置。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        RouteSettings: 规范化后的路由配置（非法值已回退默认）。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    raw = app_config.get(rc.YAML_KEY_ROUTE_SECTION, {})
    section = raw if isinstance(raw, dict) else {}
    return RouteSettings(
        mode=_read_mode(section),
        llm_confidence_threshold=_read_threshold(section),
        keywords=_read_keywords(section),
    )


def _read_mode(section: dict[str, Any]) -> str:
    """读取 mode；不在合法枚举内时回退默认 hybrid。"""
    raw = section.get(rc.YAML_KEY_ROUTE_MODE, rc.DEFAULT_ROUTE_MODE)
    return raw if raw in rc.VALID_ROUTE_MODES else rc.DEFAULT_ROUTE_MODE


def _read_threshold(section: dict[str, Any]) -> float:
    """读取 LLM 升级阈值并夹在 0~1 之间。"""
    raw = section.get(rc.YAML_KEY_LLM_CONFIDENCE_THRESHOLD)
    if not isinstance(raw, int | float):
        return rc.DEFAULT_LLM_CONFIDENCE_THRESHOLD
    return min(1.0, max(0.0, float(raw)))


def _read_keywords(section: dict[str, Any]) -> RouteKeywords:
    """读取关键词覆盖表；未配置的组保持内置默认。"""
    raw = section.get(rc.YAML_KEY_KEYWORDS, {})
    overrides = raw if isinstance(raw, dict) else {}
    defaults = RouteKeywords()
    return RouteKeywords(
        web=_read_word_list(overrides, rc.YAML_KEY_KEYWORDS_WEB, defaults.web),
        creative=_read_word_list(overrides, rc.YAML_KEY_KEYWORDS_CREATIVE, defaults.creative),
        project=_read_word_list(overrides, rc.YAML_KEY_KEYWORDS_PROJECT, defaults.project),
    )


def _read_word_list(
    overrides: dict[str, Any],
    key: str,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    """读取一组关键词；非字符串数组时回退默认。"""
    raw = overrides.get(key)
    if not isinstance(raw, list):
        return default
    words = tuple(word for word in raw if isinstance(word, str) and word)
    return words if words else default
