"""存储层包。

【职责】
    封装 PostgreSQL / Neo4j 连接与探测，不包含 LangGraph 业务逻辑。

【目录】
    postgres/  业务真相源（会话、消息、文档）
    neo4j/     派生知识图谱（Phase 2 检索）

【未配置 .env 时】
    工厂函数返回 None，health 返回 configured=False，便于本地无库开发。
"""

from app.storage.health_models import StorageHealthResult
from app.storage.neo4j.neo4j_health_checker import check_neo4j_health
from app.storage.postgres.postgres_health_checker import check_postgres_health

__all__ = [
    "StorageHealthResult",
    "check_postgres_health",
    "check_neo4j_health",
]
