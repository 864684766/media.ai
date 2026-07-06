"""路由自动扫描辅助方法。

负责发现 app/api 包下的 APIRouter 实例，供 router.py 聚合注册。
"""

import importlib
import pkgutil
from types import ModuleType

from fastapi import APIRouter

from app.core.constants import (
    API_PACKAGE_NAME,
    EXCLUDED_API_MODULES,
    ROUTER_ATTR_NAME,
)


def _is_skipped_module(module_name: str) -> bool:
    """判断模块是否应跳过扫描。

    参数:
        module_name: 模块短名称。

    返回:
        bool: 为 True 表示跳过该模块。
    """
    return module_name in EXCLUDED_API_MODULES


def _iter_api_module_names() -> list[str]:
    """遍历 app/api 包下可扫描的模块名。

    返回:
        list[str]: 按字母序排列的模块短名称列表。
    """
    api_package = importlib.import_module(API_PACKAGE_NAME)
    names = [
        info.name
        for info in pkgutil.iter_modules(api_package.__path__)
        if not _is_skipped_module(info.name)
    ]
    return sorted(names)


def _load_api_module(module_name: str) -> ModuleType:
    """按模块名加载 app/api 下的 Python 模块。

    参数:
        module_name: 模块短名称。

    返回:
        ModuleType: 已导入的模块对象。
    """
    full_module_path = f"{API_PACKAGE_NAME}.{module_name}"
    return importlib.import_module(full_module_path)


def _extract_router(module: ModuleType) -> APIRouter | None:
    """从模块中提取 APIRouter 实例。

    参数:
        module: 已导入的 API 模块。

    返回:
        APIRouter | None: 找到则返回路由实例，否则返回 None。
    """
    candidate = getattr(module, ROUTER_ATTR_NAME, None)
    if isinstance(candidate, APIRouter):
        return candidate
    return None


def discover_routers() -> list[APIRouter]:
    """扫描并收集 app/api 包下全部路由实例。

    返回:
        list[APIRouter]: 已发现的路由列表。
    """
    routers: list[APIRouter] = []
    for module_name in _iter_api_module_names():
        module = _load_api_module(module_name)
        router = _extract_router(module)
        if router is not None:
            routers.append(router)
    return routers
