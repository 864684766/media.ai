"""应用元信息工具方法。"""

from app import __version__


def get_app_version() -> str:
    """获取应用版本号。

    返回:
        str: 当前应用版本。
    """
    return __version__
