"""Skill 目录路径辅助方法。

根据 config/app.yaml 与项目根目录，定位 skills/novel-writing 等路径。
"""

from pathlib import Path

from app.core.config_paths import get_project_root
from app.core.config_yaml_loader import load_app_yaml
from app.skills import skill_constants as sc


def resolve_skills_root() -> Path:
    """解析 Skill 内容根目录的绝对路径。

    读取 config/app.yaml 的 skills.directory，默认为项目根下 skills/。

    返回:
        Path: 例如 E:/test/media.ai/skills
    """
    app_config = load_app_yaml()
    skills_section = app_config.get(sc.YAML_KEY_SKILLS_SECTION, {})
    directory_name = _read_directory_name(skills_section)
    return get_project_root() / directory_name


def build_skill_dir(skills_root: Path, directory_name: str) -> Path:
    """构造单个 Skill 文件夹路径。

    参数:
        skills_root: skills 根目录。
        directory_name: 子文件夹名，如 novel-writing。

    返回:
        Path: 单个 Skill 目录绝对路径。
    """
    return skills_root / directory_name


def build_skill_md_path(skill_dir: Path) -> Path:
    """构造 SKILL.md 文件路径。

    参数:
        skill_dir: 单个 Skill 目录。

    返回:
        Path: SKILL.md 绝对路径。
    """
    return skill_dir / sc.SKILL_MD_FILENAME


def build_system_prompt_path(skill_dir: Path) -> Path:
    """构造 prompts/system.md 文件路径。

    参数:
        skill_dir: 单个 Skill 目录。

    返回:
        Path: system prompt 文件绝对路径。
    """
    return skill_dir / sc.SYSTEM_PROMPT_RELATIVE_PATH


def is_auto_discover_enabled() -> bool:
    """读取 skills.auto_discover 开关。

    行为约定：
        true（默认）: load_skill 未指定 skill_id 时按 triggers 自动匹配；
        false: 只有请求显式传 skill_id 才加载 Skill，不做自动匹配。

    返回:
        bool: 配置值；缺失或类型错误时为 True。
    """
    app_config = load_app_yaml()
    skills_section = app_config.get(sc.YAML_KEY_SKILLS_SECTION, {})
    if not isinstance(skills_section, dict):
        return sc.DEFAULT_AUTO_DISCOVER
    raw = skills_section.get(sc.YAML_KEY_SKILLS_AUTO_DISCOVER, sc.DEFAULT_AUTO_DISCOVER)
    return raw if isinstance(raw, bool) else sc.DEFAULT_AUTO_DISCOVER


def _read_directory_name(skills_section: object) -> str:
    """从 app.yaml skills 段读取 directory 字段。

    参数:
        skills_section: app.yaml 中 skills 键对应的值。

    返回:
        str: 目录名，缺省为 skills。
    """
    if not isinstance(skills_section, dict):
        return sc.DEFAULT_SKILLS_DIRECTORY
    raw = skills_section.get(sc.YAML_KEY_SKILLS_DIRECTORY, sc.DEFAULT_SKILLS_DIRECTORY)
    if not isinstance(raw, str) or not raw.strip():
        return sc.DEFAULT_SKILLS_DIRECTORY
    return raw.strip()
