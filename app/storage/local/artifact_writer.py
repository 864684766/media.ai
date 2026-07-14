"""本地 artifact 写入。"""

from pathlib import Path


def write_text_file(path: Path, content: str) -> Path:
    """写入 UTF-8 文本文件并创建父目录。

    参数:
        path: 目标路径。
        content: 文本内容。

    返回:
        Path: 已写入路径。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
