"""Neo4j Driver 单例工厂。

每次 API 请求若新建 Driver 会耗尽远程 Neo4j 连接数；全局复用同一连接池。
"""

from threading import Lock

from neo4j import Driver

from app.storage.neo4j.neo4j_driver_builder import build_neo4j_driver
from app.storage.neo4j.neo4j_settings_reader import get_neo4j_auth, get_neo4j_uri

_driver: Driver | None = None
_driver_lock = Lock()


def get_shared_neo4j_driver() -> Driver | None:
    """返回进程内共享 Driver；未配置 Neo4j 时 None。"""
    global _driver
    uri = get_neo4j_uri()
    auth = get_neo4j_auth()
    if uri is None or auth is None:
        return None
    if _driver is not None:
        return _driver
    with _driver_lock:
        if _driver is None:
            _driver = build_neo4j_driver(uri, auth)
        return _driver


def reset_shared_neo4j_driver() -> None:
    """测试或进程退出时释放共享 Driver 并重置单例。"""
    global _driver
    with _driver_lock:
        if _driver is not None:
            _driver.close()
            _driver = None
