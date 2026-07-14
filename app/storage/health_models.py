"""存储层健康检查结果模型。

供 postgres / neo4j 的 health 函数返回统一结构，便于 API 或日志展示。
"""

from pydantic import BaseModel, Field


class StorageHealthResult(BaseModel):
    """单次存储连通性检查结果。

    参数说明:
        backend: 存储类型标识，如 postgres / neo4j。
        configured: .env 是否提供了连接配置。
        reachable: 是否成功连上并执行探测语句。
        message: 人类可读说明（中文）。
    """

    backend: str = Field(description="存储后端名称")
    configured: bool = Field(description="是否已在 .env 配置连接信息")
    reachable: bool = Field(description="探测是否成功")
    message: str = Field(default="", description="状态说明")
