"""Skill Registry 模块常量。

集中存放文件名、配置键名等字面量，避免散落在各 loader 中。
"""

# config/app.yaml 中 skills 段键名
YAML_KEY_SKILLS_SECTION = "skills"
YAML_KEY_SKILLS_DIRECTORY = "directory"
YAML_KEY_SKILLS_AUTO_DISCOVER = "auto_discover"

# 默认 Skill 内容根目录（相对项目根）
DEFAULT_SKILLS_DIRECTORY = "skills"

# auto_discover 默认值：未配置时开启自动匹配
DEFAULT_AUTO_DISCOVER = True

# Skill 目录内固定文件名
SKILL_MD_FILENAME = "SKILL.md"
SYSTEM_PROMPT_RELATIVE_PATH = "prompts/system.md"

# SKILL.md frontmatter 中常用字段
FRONTMATTER_KEY_NAME = "name"
FRONTMATTER_KEY_DESCRIPTION = "description"
FRONTMATTER_KEY_METADATA = "metadata"
METADATA_KEY_SKILL_ID = "skill_id"
METADATA_KEY_DISPLAY_NAME = "display_name"
METADATA_KEY_TRIGGERS = "triggers"

# 匹配不到 Skill 时的默认 id
DEFAULT_SKILL_ID = "novel-writing"
