"""Skill Registry：扫描根目录 skills/ 并加载 SkillContext。

【本文件职责】
    「通用人设扫描器」入口：不负责写作家/剪辑师内容，只负责找到并读出它们。

【数据从哪来、到哪去】
    读  根目录 skills/*/SKILL.md、prompts/system.md（内容）
    写  SkillContext → 将来由 load_skill 节点放进 state.skill.system_prompt

【与 state.prompt 的区别】
    本模块只产出 system_prompt（固定人设）；
    state.prompt 是 compact_history  later 拼好的整轮输入，不是本文件管的。

【调用示例】
    load_skill_context(skill_id="novel-writing")
    load_skill_context(user_message="帮我续写打斗")  # trigger 匹配

【标准】
    Skill 内容格式对齐 Agent Skills（agentskills.io）；加载逻辑在本 Python 包。
"""

from pathlib import Path

from app.skills import skill_constants as sc
from app.skills.skill_frontmatter_parser import extract_skill_definition, parse_skill_frontmatter
from app.skills.creation_type_filter import filter_skills_by_creation_type
from app.skills.skill_matcher import match_skill_definition
from app.skills.skill_models import SkillContext, SkillDefinition
from app.skills.skill_path_helper import (
    build_skill_dir,
    build_skill_md_path,
    is_auto_discover_enabled,
    resolve_skills_root,
)
from app.skills.skill_system_prompt_loader import load_system_prompt_text


def discover_skills() -> list[SkillDefinition]:
    """扫描 config 指定的 skills 目录，发现所有 */SKILL.md。

    返回:
        list[SkillDefinition]: 已解析的 Skill 元数据列表。
    """
    skills_root = resolve_skills_root()
    if not skills_root.is_dir():
        return []
    return _scan_skill_directories(skills_root)


def load_skill_context(
    skill_id: str | None = None,
    user_message: str = "",
    creation_type: str | None = None,
) -> SkillContext:
    """加载 SkillContext，供 load_skill 节点写入 state.skill。

    参数:
        skill_id: 可选，客户端指定 Skill；None 则自动匹配。
        user_message: 用户消息，供 triggers 匹配。
        creation_type: 创作类型 novel / video，限定候选 Skill 池。

    返回:
        SkillContext: 含 id、display_name、system_prompt。
    """
    # 步骤 0：auto_discover=false 且未显式指定 skill_id 时，不做自动匹配
    if skill_id is None and not is_auto_discover_enabled():
        return _empty_skill_context()
    # 步骤 1：列出所有已注册 Skill（新增文件夹会自动出现，一般不用改 Python）
    skills = discover_skills()
    skills = filter_skills_by_creation_type(skills, creation_type)
    # 步骤 2：优先 skill_id，其次 trigger 词，最后列表第一个
    chosen = match_skill_definition(skills, skill_id, user_message)
    if chosen is None:
        return _empty_skill_context()
    # 步骤 3：读 prompts/system.md 全文 → system_prompt
    return _build_skill_context(chosen)


def _scan_skill_directories(skills_root: Path) -> list[SkillDefinition]:
    """遍历 skills 下每个子目录并解析 SKILL.md。"""
    results: list[SkillDefinition] = []
    for child in sorted(skills_root.iterdir()):
        if not child.is_dir():
            continue
        definition = _parse_skill_directory(child)
        if definition is not None:
            results.append(definition)
    return results


def _parse_skill_directory(skill_dir: Path) -> SkillDefinition | None:
    """解析单个 Skill 子目录。"""
    skill_md_path = build_skill_md_path(skill_dir)
    if not skill_md_path.is_file():
        return None
    raw_text = skill_md_path.read_text(encoding="utf-8")
    frontmatter = parse_skill_frontmatter(raw_text)
    return extract_skill_definition(frontmatter, skill_dir.name)


def _build_skill_context(definition: SkillDefinition) -> SkillContext:
    """根据 SkillDefinition 读取 system.md 并组装 SkillContext。"""
    skills_root = resolve_skills_root()
    skill_dir = build_skill_dir(skills_root, definition.directory_name)
    system_prompt = load_system_prompt_text(skill_dir)
    return SkillContext(
        id=definition.skill_id,
        display_name=definition.display_name,
        system_prompt=system_prompt,
    )


def _empty_skill_context() -> SkillContext:
    """无 Skill 可加载时的空上下文（兜底，避免节点崩溃）。"""
    return SkillContext(id=sc.DEFAULT_SKILL_ID, display_name="", system_prompt="")
