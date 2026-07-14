"""Neo4j Driver 构建（连接池参数）。"""

from neo4j import Driver, GraphDatabase

from app.storage.neo4j import neo4j_constants as nc


def build_neo4j_driver(uri: str, auth: tuple[str, str]) -> Driver:
    """使用项目默认连接池参数构建 Driver。

    参数:
        uri: Bolt 地址。
        auth: (user, password) 元组。

    返回:
        Driver: 可复用的 Neo4j 驱动实例。
    """
    return GraphDatabase.driver(
        uri,
        auth=auth,
        max_connection_lifetime=nc.NEO4J_DRIVER_MAX_CONNECTION_LIFETIME,
        max_connection_pool_size=nc.NEO4J_MAX_CONNECTION_POOL_SIZE,
    )
