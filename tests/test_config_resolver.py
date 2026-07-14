"""ConfigResolver 单元测试。"""

from pathlib import Path

import pytest

from app.core import config_constants as cc
from app.core.config_resolver import resolve
from app.core.config_resolver_clamp import clamp_runtime_values
from app.core.config_resolver_merge import merge_runtime_overrides
from app.core.config_yaml_loader import load_app_yaml


def test_load_app_yaml_has_dev_profile() -> None:
    """验证 config/app.yaml 可被加载且 profile 为 dev。"""
    data = load_app_yaml()
    assert data.get(cc.YAML_KEY_PROFILE) == cc.PROFILE_DEV


def test_resolve_default_dev_profile() -> None:
    """默认 app.yaml 应解析为 dev Profile 参数。"""
    runtime = resolve({"profile": cc.PROFILE_DEV})
    assert runtime.profile == cc.PROFILE_DEV
    assert runtime.max_retries == 2
    assert runtime.retrieve_top_k == 30
    assert runtime.refuse_when_no_evidence is False


def test_resolve_strict_profile() -> None:
    """strict Profile 应启用 refuse_when_no_evidence。"""
    runtime = resolve({"profile": cc.PROFILE_STRICT})
    assert runtime.profile == cc.PROFILE_STRICT
    assert runtime.refuse_when_no_evidence is True
    assert runtime.rerank_top_k == 3


def test_resolve_unknown_profile_falls_back_to_dev() -> None:
    """未知 profile 名应回退 dev 预设。"""
    runtime = resolve({"profile": "unknown-profile"})
    assert runtime.profile == cc.PROFILE_DEV
    assert runtime.retrieve_top_k == 30


def test_clamp_max_retries_hard_cap() -> None:
    """max_retries 不得超过 L1 硬上限。"""
    merged = merge_runtime_overrides(
        {cc.FIELD_MAX_RETRIES: 2},
        {cc.FIELD_MAX_RETRIES: 99},
    )
    clamped = clamp_runtime_values(merged)
    assert clamped[cc.FIELD_MAX_RETRIES] == cc.MAX_RETRIES_HARD_CAP


def test_resolve_with_override_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """config.override.yaml 应覆盖 Profile 预设中的 Runtime 字段。"""
    override_path = tmp_path / "config.override.yaml"
    override_path.write_text("max_retries: 4\nretrieve_top_k: 80\n", encoding="utf-8")
    monkeypatch.setattr(
        "app.core.config_resolver.load_override_yaml_if_exists",
        lambda: {"max_retries": 4, "retrieve_top_k": 80},
    )
    runtime = resolve({"profile": cc.PROFILE_DEV})
    assert runtime.max_retries == 4
    assert runtime.retrieve_top_k == 80
