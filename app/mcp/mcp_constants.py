"""MCP 配置常量。

【职责】
    集中管理 config/app.yaml 中 mcp 段的键名与默认值，
    代码里不出现裸字符串键。
"""

# app.yaml 顶层段名：mcp
YAML_KEY_MCP_SECTION = "mcp"

# mcp.enabled：是否启用 MCP（第一版默认 false）
YAML_KEY_ENABLED = "enabled"

# mcp.servers：MCP Server 列表（Phase 3 使用，当前为空列表占位）
YAML_KEY_SERVERS = "servers"

# 未配置时的默认值：不启用
DEFAULT_ENABLED = False

# MCP 未启用时调用工具的报错文案
MCP_DISABLED_MESSAGE = "MCP 未启用：请在 config/app.yaml 设置 mcp.enabled: true（Phase 3 功能）"
