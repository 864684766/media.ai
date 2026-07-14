"""Skill 相关数据模型。

定义 Registry 扫描结果与 load_skill 写入 state 的 SkillContext 结构。
"""

from pydantic import BaseModel, Field

from app.skills import skill_constants as sc


class SkillDefinition(BaseModel):
    """单个 Skill 的元数据（来自 skills/*/SKILL.md frontmatter）。

    参数说明:
        skill_id: 唯一标识，如 novel-writing。
        display_name: 展示名，如「资深玄幻小说作家」。
        description: Skill 简介，供匹配或文档展示。
        triggers: 触发词列表，用户消息含这些词时可自动匹配。
        directory_name: skills 下的文件夹名，与 skill_id 通常一致。
    """

    skill_id: str
    display_name: str = Field(default="")
    description: str = Field(default="")
    triggers: list[str] = Field(default_factory=list)
    directory_name: str = Field(default="")


class SkillContext(BaseModel):
    """load_skill 节点写入 AgentState.skill 的结构（Phase 1 契约预览）。

    参数说明:
        id: 当前生效的 skill_id。
        display_name: 展示名。
        system_prompt: 从 prompts/system.md 读取的 system 角色文本。
    """

    id: str = Field(default=sc.DEFAULT_SKILL_ID)
    display_name: str = Field(default="")
    system_prompt: str = Field(default="")
