"""MCP 工具模型。"""

from pydantic import BaseModel, Field


class McpToolDefinition(BaseModel):
    """MCP 工具定义。

    参数说明:
        name: 工具名。
        description: 工具说明。
        skill_id: 所属 Skill id。
    """

    name: str = Field(description="工具名")
    description: str = Field(default="", description="工具说明")
    skill_id: str = Field(default="", description="所属 Skill")
