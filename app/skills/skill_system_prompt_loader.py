"""System prompt 文件加载器。

从 skills/*/prompts/system.md 读取文本，供 SkillContext 使用。
"""

from pathlib import Path

from app.skills.skill_path_helper import build_system_prompt_path


def load_system_prompt_text(skill_dir: Path) -> str:
    """读取单个 Skill 的 prompts/system.md 内容。

    参数:
        skill_dir: 例如 skills/novel-writing/ 的绝对路径。

    返回:
        str: 文件全文；文件不存在时返回空字符串。
    """
    prompt_path = build_system_prompt_path(skill_dir)
    if not prompt_path.is_file():
        return ""
    return prompt_path.read_text(encoding="utf-8").strip()
