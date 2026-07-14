"""YAML 配置文件加载器。

【本文件职责】
    把磁盘上的 .yaml 文件读成 Python 字典，供 ConfigResolver 使用。

【读哪些文件】
    config/app.yaml              必有，运维主配置
    config/config.override.yaml  可选，不存在则返回 {}

【何时调用】
    config_resolver.resolve() 第一步（若未传入现成字典）会 load_app_yaml()

【示例】
    load_app_yaml() → {"profile": "dev", "model": {"provider": "zhipu", ...}}
"""

from pathlib import Path
from typing import Any

import yaml

from app.core.config_paths import get_app_yaml_path, get_override_yaml_path


def load_yaml_file(path: Path) -> dict[str, Any]:
    """读取并解析单个 YAML 文件。

    参数:
        path: YAML 文件的绝对路径。

    返回:
        dict[str, Any]: 解析后的字典；空文件返回 {}。

    异常:
        FileNotFoundError: 文件不存在时抛出。
    """
    raw_text = path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(raw_text)
    return parsed if isinstance(parsed, dict) else {}


def load_app_yaml() -> dict[str, Any]:
    """加载默认运维配置 config/app.yaml。

    返回:
        dict[str, Any]: app.yaml 完整内容（含 model、skills 等段）。
    """
    return load_yaml_file(get_app_yaml_path())


def load_override_yaml_if_exists() -> dict[str, Any]:
    """加载可选的高级覆盖 config.override.yaml。

    返回:
        dict[str, Any]: 覆盖内容；文件不存在时返回 {}，不报错。
    """
    override_path = get_override_yaml_path()
    if not override_path.is_file():
        return {}
    return load_yaml_file(override_path)
