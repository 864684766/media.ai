"""MCP（Model Context Protocol）模块。

【职责】
    Agent 通过 MCP 以统一协议调用外部工具（存稿、导出、ASR、TTS 等）。
    设计详见 docs/ARCHITECTURE.html sec-11。

【当前阶段】
    Phase 1 空 Stub：只读取 config/app.yaml 的 mcp 段并提供 Client 接口骨架；
    真实 MCP Server 连接与 ToolNode 集成在 Phase 3 落地。
"""

from app.mcp.client import McpClient, build_mcp_client

__all__ = ["McpClient", "build_mcp_client"]
