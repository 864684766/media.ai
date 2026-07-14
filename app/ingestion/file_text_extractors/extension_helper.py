"""上传文件名扩展名解析。"""

from pathlib import PurePosixPath


def resolve_extension(filename: str) -> str:
    """从文件名解析小写扩展名（含点）。

    参数:
        filename: 原始文件名。

    返回:
        str: 如 ``.txt``；无扩展名时返回空串。
    """
    suffix = PurePosixPath(filename).suffix.lower()
    return suffix
