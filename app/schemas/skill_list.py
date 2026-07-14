"""Skill 列表 API 响应契约。

【职责】
    定义 GET /skills 的响应结构，供前端 Skill 下拉选择器消费。
"""

from pydantic import BaseModel, Field


class SkillListItem(BaseModel):
    """Skill 列表单项（不含 system_prompt 全文，避免响应过大）。"""

    id: str = Field(description="Skill id，如 novel-writing")
    display_name: str = Field(default="", description="展示名")
    description: str = Field(default="", description="简介")
    triggers: list[str] = Field(default_factory=list, description="自动匹配触发词")


class SkillListResponse(BaseModel):
    """Skill 列表响应。"""

    items: list[SkillListItem] = Field(default_factory=list)
