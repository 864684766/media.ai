"""Ingestion 配置读取器。

【职责】
    从 config/app.yaml 的 ingestion 段读取 chunk_size、chunk_overlap、dry_run_default。
"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml
from app.ingestion import ingestion_constants as ic


def load_ingestion_settings(yaml_config: dict[str, Any] | None = None) -> dict[str, int | bool]:
    """读取 Ingestion 配置。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        dict[str, int | bool]: 规范化后的配置。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    section = _read_ingestion_section(app_config)
    return {
        ic.YAML_KEY_CHUNK_SIZE: _read_int(section, ic.YAML_KEY_CHUNK_SIZE, ic.DEFAULT_CHUNK_SIZE),
        ic.YAML_KEY_CHUNK_OVERLAP: _read_int(section, ic.YAML_KEY_CHUNK_OVERLAP, ic.DEFAULT_CHUNK_OVERLAP),
        ic.YAML_KEY_DRY_RUN_DEFAULT: _read_bool(section, ic.YAML_KEY_DRY_RUN_DEFAULT),
    }


def load_embedding_settings(yaml_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """读取 ingestion.embedding 子段配置。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        dict: {"provider": str, "dimension": int}。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    section = _read_ingestion_section(app_config)
    raw = section.get(ic.YAML_KEY_EMBEDDING_SECTION, {})
    embedding = raw if isinstance(raw, dict) else {}
    provider = embedding.get(ic.YAML_KEY_EMBEDDING_PROVIDER, ic.DEFAULT_EMBEDDING_PROVIDER)
    return {
        ic.YAML_KEY_EMBEDDING_PROVIDER: provider if isinstance(provider, str) else ic.DEFAULT_EMBEDDING_PROVIDER,
        ic.YAML_KEY_EMBEDDING_DIMENSION: _read_int(
            embedding, ic.YAML_KEY_EMBEDDING_DIMENSION, ic.DEFAULT_EMBEDDING_DIMENSION
        ),
    }


def _read_ingestion_section(app_config: dict[str, Any]) -> dict[str, Any]:
    """读取 ingestion 段。"""
    raw = app_config.get(ic.YAML_KEY_INGESTION_SECTION, {})
    return raw if isinstance(raw, dict) else {}


def _read_int(section: dict[str, Any], key: str, default: int) -> int:
    """读取正整数配置。"""
    raw = section.get(key, default)
    value = int(raw) if isinstance(raw, int | str) else default
    return max(1, value)


def _read_bool(section: dict[str, Any], key: str) -> bool:
    """读取布尔配置。"""
    raw = section.get(key, ic.DEFAULT_DRY_RUN)
    return raw if isinstance(raw, bool) else ic.DEFAULT_DRY_RUN
