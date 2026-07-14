"""SKILL.md frontmatter 解析器。

只解析文件开头 --- 之间的 YAML，不处理正文 Markdown。
"""

from typing import Any

import yaml

from app.skills import skill_constants as sc


def parse_skill_frontmatter(skill_md_text: str) -> dict[str, Any]:
    """从 SKILL.md 全文提取 frontmatter 字典。

    参数:
        skill_md_text: SKILL.md 完整文本。

    返回:
        dict[str, Any]: frontmatter 字段；格式非法时返回 {}。
    """
    parts = skill_md_text.split("---")
    if len(parts) < 3:
        return {}
    yaml_block = parts[1].strip()
    parsed = yaml.safe_load(yaml_block)
    return parsed if isinstance(parsed, dict) else {}


def extract_skill_definition(
    frontmatter: dict[str, Any],
    directory_name: str,
) -> "SkillDefinition | None":
    """将 frontmatter 转为 SkillDefinition。

    参数:
        frontmatter: parse_skill_frontmatter 的结果。
        directory_name: skills 子目录名。

    返回:
        SkillDefinition | None: 解析成功返回模型；缺少 skill_id 时返回 None。
    """
    from app.skills.skill_models import SkillDefinition

    metadata = frontmatter.get(sc.FRONTMATTER_KEY_METADATA, {})
    if not isinstance(metadata, dict):
        metadata = {}
    skill_id = _read_skill_id(metadata, frontmatter, directory_name)
    if not skill_id:
        return None
    return SkillDefinition(
        skill_id=skill_id,
        display_name=_read_display_name(metadata, skill_id),
        description=_read_description(frontmatter),
        triggers=_read_triggers(metadata),
        directory_name=directory_name,
    )


def _read_skill_id(
    metadata: dict[str, Any],
    frontmatter: dict[str, Any],
    directory_name: str,
) -> str:
    """读取 skill_id，优先 metadata.skill_id，其次 name，再次目录名。"""
    raw = metadata.get(sc.METADATA_KEY_SKILL_ID)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    name = frontmatter.get(sc.FRONTMATTER_KEY_NAME)
    if isinstance(name, str) and name.strip():
        return name.strip()
    return directory_name


def _read_display_name(metadata: dict[str, Any], skill_id: str) -> str:
    """读取展示名，缺省用 skill_id。"""
    raw = metadata.get(sc.METADATA_KEY_DISPLAY_NAME)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return skill_id


def _read_description(frontmatter: dict[str, Any]) -> str:
    """读取 description 字段。"""
    raw = frontmatter.get(sc.FRONTMATTER_KEY_DESCRIPTION)
    if isinstance(raw, str):
        return raw.strip()
    return ""


def _read_triggers(metadata: dict[str, Any]) -> list[str]:
    """读取 triggers 列表。"""
    raw = metadata.get(sc.METADATA_KEY_TRIGGERS, [])
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]
