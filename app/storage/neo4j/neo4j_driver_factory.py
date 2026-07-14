"""Neo4j Driver 工厂。

未配置 NEO4J 时返回 None；已配置时返回进程内共享 Driver。
"""

from neo4j import Driver

from app.storage.neo4j.neo4j_driver_singleton import get_shared_neo4j_driver


def create_neo4j_driver() -> Driver | None:
    """根据 .env 返回共享 Neo4j Driver。

    返回:
        Driver | None: 未配置 URI/密码时返回 None。
    """
    return get_shared_neo4j_driver()
