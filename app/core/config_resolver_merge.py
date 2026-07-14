"""ConfigResolver 辅助：Profile 名称提取与字典合并。

【本文件职责】
    1. 从 app.yaml 读出 profile: dev|prod|strict
    2. 拷贝对应套餐字典（避免改坏全局 PROFILE_PRESETS）
    3. 把 override 文件里的 Runtime 字段盖到套餐上

【合并规则】
    只覆盖 RuntimeConfig 认识的键（max_retries 等），忽略 model、skills 等其它段
    例：override 写 max_retries: 4 → 仅改重试次数，不改 retrieve_top_k
"""

from typing import Any

from app.core import config_constants as cc
from app.core.profile_presets import PROFILE_PRESETS


def extract_profile_name(yaml_config: dict[str, Any]) -> str:
    """从 app.yaml 字典中读取 profile 字段。

    参数:
        yaml_config: 已加载的 app.yaml 内容。

    返回:
        str: Profile 名称；缺省或未知时回退为 dev。
    """
    raw = yaml_config.get(cc.YAML_KEY_PROFILE, cc.DEFAULT_PROFILE)
    if not isinstance(raw, str):
        return cc.DEFAULT_PROFILE
    normalized = raw.strip().lower()
    # 防止 typo：profile: production 不在表里 → 安全回退 dev
    if normalized not in PROFILE_PRESETS:
        return cc.DEFAULT_PROFILE
    return normalized


def copy_profile_preset(profile_name: str) -> dict[str, Any]:
    """复制指定 Profile 的预设字典（避免修改全局常量）。

    参数:
        profile_name: dev / prod / strict。

    返回:
        dict[str, Any]: 预设参数的浅拷贝。
    """
    preset = PROFILE_PRESETS[profile_name]
    return dict(preset)


def merge_runtime_overrides(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """将 override 中的 Runtime 字段合并进 base（仅覆盖已知键）。

    参数:
        base: Profile 预设或已合并的字典。
        override: config.override.yaml 或测试注入的覆盖项。

    返回:
        dict[str, Any]: 合并后的新字典（不修改入参）。
    """
    merged = dict(base)
    runtime_keys = _runtime_field_names()
    for key in runtime_keys:
        if key in override:
            merged[key] = override[key]
    return merged


def _runtime_field_names() -> tuple[str, ...]:
    """返回 RuntimeConfig 可覆盖字段名集合。

    返回:
        tuple[str, ...]: 字段名元组。
    """
    return (
        cc.FIELD_MAX_RETRIES,
        cc.FIELD_RETRIEVE_TOP_K,
        cc.FIELD_RERANK_TOP_K,
        cc.FIELD_GRAPH_EXPAND_HOPS,
        cc.FIELD_WEB_SEARCH,
        cc.FIELD_REFUSE_WHEN_NO_EVIDENCE,
    )
