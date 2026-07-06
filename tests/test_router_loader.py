"""路由自动扫描测试。"""

from fastapi import APIRouter

from app.api.router_loader import discover_routers
from app.core.constants import CHAT_ROUTE_PREFIX


def test_discover_routers_includes_chat() -> None:
    """验证自动扫描能发现 chat 路由模块。

    断言:
        - 至少发现一个路由
        - chat 路由前缀正确
    """
    routers = discover_routers()
    assert len(routers) >= 1
    assert _has_chat_prefix(routers)


def _has_chat_prefix(routers: list[APIRouter]) -> bool:
    """检查路由列表中是否包含 chat 前缀。

    参数:
        routers: 已扫描到的路由列表。

    返回:
        bool: 存在 chat 前缀时为 True。
    """
    for router in routers:
        if router.prefix == CHAT_ROUTE_PREFIX:
            return True
    return False
