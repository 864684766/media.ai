"""creative 配置读取（澄清/大纲）。"""

from dataclasses import dataclass

from app.core.clarification_constants import (
    DEFAULT_CLARIFICATION_MAX_ROUNDS,
    DEFAULT_MIN_BRIEF_CHARS,
    DEFAULT_QUESTIONS_PER_ROUND_MAX,
)
from app.core.creative_plan_constants import (
    DEFAULT_OUTLINE_AUTO_APPROVE,
    DEFAULT_OUTLINE_ENABLED,
    DEFAULT_OUTLINE_MAX_REVISIONS,
    DEFAULT_OUTLINE_REQUIRES_CLARIFICATION,
)
from app.core.config_yaml_loader import load_app_yaml


@dataclass(frozen=True)
class OutlineConfig:
    """大纲 HITL 配置。"""

    enabled: bool
    requires_clarification: bool
    auto_approve: bool
    max_revisions: int


@dataclass(frozen=True)
class ClarificationConfig:
    """澄清引导配置。"""

    enabled: bool
    max_rounds: int
    questions_per_round_max: int
    allow_skip: bool
    min_brief_chars: int


def load_clarification_config() -> ClarificationConfig:
    """从 app.yaml 读取 creative.clarification。"""
    root = load_app_yaml()
    creative = root.get("creative", {}) if isinstance(root, dict) else {}
    block = creative.get("clarification", {}) if isinstance(creative, dict) else {}
    return ClarificationConfig(
        enabled=bool(block.get("enabled", True)),
        max_rounds=int(block.get("max_rounds", DEFAULT_CLARIFICATION_MAX_ROUNDS)),
        questions_per_round_max=int(
            block.get("questions_per_round_max", DEFAULT_QUESTIONS_PER_ROUND_MAX),
        ),
        allow_skip=bool(block.get("allow_skip", True)),
        min_brief_chars=int(block.get("min_brief_chars", DEFAULT_MIN_BRIEF_CHARS)),
    )


def load_outline_config() -> OutlineConfig:
    """从 app.yaml 读取 creative.outline。"""
    root = load_app_yaml()
    creative = root.get("creative", {}) if isinstance(root, dict) else {}
    block = creative.get("outline", {}) if isinstance(creative, dict) else {}
    return OutlineConfig(
        enabled=bool(block.get("enabled", DEFAULT_OUTLINE_ENABLED)),
        requires_clarification=bool(
            block.get("requires_clarification", DEFAULT_OUTLINE_REQUIRES_CLARIFICATION),
        ),
        auto_approve=bool(block.get("auto_approve", DEFAULT_OUTLINE_AUTO_APPROVE)),
        max_revisions=int(block.get("max_revisions", DEFAULT_OUTLINE_MAX_REVISIONS)),
    )
