"""history 配置读取器。

【职责】
    从 config/app.yaml 的 history 段读取 retention_days，
    供 load_history 只加载保留期内的消息（sec-14.3 历史保留策略）。
"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml

# app.yaml 顶层段名与键名
YAML_KEY_HISTORY_SECTION = "history"
YAML_KEY_RETENTION_DAYS = "retention_days"

# 默认保留天数：约 3 个月
DEFAULT_RETENTION_DAYS = 90


def load_history_retention_days(yaml_config: dict[str, Any] | None = None) -> int:
    """读取会话消息保留天数。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        int: 保留天数；缺失或非法时为 90。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    raw = app_config.get(YAML_KEY_HISTORY_SECTION, {})
    section = raw if isinstance(raw, dict) else {}
    days = section.get(YAML_KEY_RETENTION_DAYS, DEFAULT_RETENTION_DAYS)
    if isinstance(days, int) and days > 0:
        return days
    return DEFAULT_RETENTION_DAYS
