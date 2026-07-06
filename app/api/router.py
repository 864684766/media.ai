"""路由聚合。

自动扫描 app/api 包下的路由模块并完成注册。
"""

from fastapi import APIRouter

from app.api.router_loader import discover_routers


def build_api_router() -> APIRouter:
    """构建并返回聚合后的 API 路由。

    返回:
        APIRouter: 已挂载全部子路由的总路由。
    """
    api_router = APIRouter()
    for router in discover_routers():
        api_router.include_router(router)
    return api_router


api_router = build_api_router()
