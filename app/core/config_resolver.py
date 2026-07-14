"""ConfigResolver：将 YAML + Profile + 覆盖合并为 RuntimeConfig。

【本文件职责】
    配置体系的「总入口」：把分散的配置源合成一个 RuntimeConfig 对象。

【处理流程】（与 ARCHITECTURE sec-08 伪代码一致）
    ① 读 app.yaml（或调用方传入的字典）
    ② 读 profile 键 → 选 dev/prod/strict 套餐
    ③ 拷贝该套餐的默认数字
    ④ 若存在 config.override.yaml → 覆盖部分 Runtime 字段
    ⑤ L1 clamp → 防止危险超大值
    ⑥ 封装为 RuntimeConfig → 交给 LangGraph state.runtime_config

【调用示例】
    from app.core.config_resolver import resolve
    cfg = resolve()                    # 读 config/app.yaml
    cfg = resolve({"profile": "strict"})  # 测试时可传入假 YAML

【注意】
    本函数目前只解析 Profile 相关 Runtime 字段；
    app.yaml 里的 model、skills 等段由其它模块直接读 YAML 或后续扩展。
"""

from typing import Any

from app.core import config_constants as cc
from app.core.config_resolver_clamp import clamp_runtime_values
from app.core.config_resolver_merge import (
    copy_profile_preset,
    extract_profile_name,
    merge_runtime_overrides,
)
from app.core.config_yaml_loader import load_app_yaml, load_override_yaml_if_exists
from app.core.runtime_config import RuntimeConfig


def resolve(yaml_config: dict[str, Any] | None = None) -> RuntimeConfig:
    """解析运行时配置（Phase 1 第 1 周核心入口）。

    参数:
        yaml_config: 已加载的 app.yaml；为 None 时从默认路径读取。

    返回:
        RuntimeConfig: 供 LangGraph state 挂载的只读配置对象。
    """
    # 步骤 1：取得 app.yaml 内容（文件或测试传入）
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    # 步骤 2：例如 profile: dev → "dev"
    profile_name = extract_profile_name(app_config)
    # 步骤 3：从 PROFILE_PRESETS 拷贝 dev 档默认数
    base_values = copy_profile_preset(profile_name)
    # 步骤 4：高级运维 optional 覆盖（无文件则为 {}）
    override_values = load_override_yaml_if_exists()
    merged = merge_runtime_overrides(base_values, override_values)
    # 步骤 5：L1 安全阀，例如 max_retries 不超过 5
    clamped = clamp_runtime_values(merged)
    # 步骤 6：把套餐名也放进结果，便于日志与调试
    clamped[cc.FIELD_PROFILE] = profile_name
    return RuntimeConfig(**clamped)
