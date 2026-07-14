"""Neo4j 连接配置读取。"""

from app.core.config import settings


def is_neo4j_configured() -> bool:
    """判断 .env 是否提供了 NEO4J_URI。

    返回:
        bool: URI 非空时为 True。
    """
    uri = settings.neo4j_uri
    return isinstance(uri, str) and bool(uri.strip())


def get_neo4j_uri() -> str | None:
    """读取 Neo4j Bolt URI。"""
    if not is_neo4j_configured():
        return None
    return settings.neo4j_uri.strip()


def get_neo4j_auth() -> tuple[str, str] | None:
    """读取 Neo4j 用户名与密码元组。

    返回:
        tuple[str, str] | None: 未配置 URI 或密码时返回 None。
    """
    if not is_neo4j_configured():
        return None
    password = settings.neo4j_password
    if password is None or not str(password).strip():
        return None
    return settings.neo4j_user, str(password).strip()
