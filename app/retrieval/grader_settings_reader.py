"""Grader 配置读取器。

【职责】
    从 config/app.yaml grader 段读取 mode（rule / llm / hybrid）。
"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml
from app.retrieval import grader_constants as gc


def load_grader_mode(yaml_config: dict[str, Any] | None = None) -> str:
    """读取 Grader 模式。

    参数:
        yaml_config: 测试可传入假配置；None 时读真实 app.yaml。

    返回:
        str: rule / llm / hybrid；非法值回退 hybrid。
    """
    config = yaml_config if yaml_config is not None else load_app_yaml()
    section = config.get(gc.YAML_KEY_GRADER_SECTION, {})
    if not isinstance(section, dict):
        return gc.DEFAULT_GRADER_MODE
    mode = str(section.get(gc.YAML_KEY_GRADER_MODE, gc.DEFAULT_GRADER_MODE))
    if mode in (gc.GRADER_MODE_RULE, gc.GRADER_MODE_LLM, gc.GRADER_MODE_HYBRID):
        return mode
    return gc.DEFAULT_GRADER_MODE
