"""ffmpeg 可执行文件解析（V7）。

【职责】
    解析 FFMPEG_PATH 环境变量或 PATH 中的 ffmpeg 二进制。

【何时调用】
    local_ffmpeg clip/compose 写入前检测可用性。
"""

import os
import shutil
from pathlib import Path


def resolve_ffmpeg_binary() -> str | None:
    """返回 ffmpeg 绝对路径；不可用则 None。"""
    env_path = os.environ.get("FFMPEG_PATH", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_file():
            return str(candidate.resolve())
    found = shutil.which("ffmpeg")
    return found


def is_ffmpeg_available() -> bool:
    """系统是否可调用 ffmpeg。"""
    return resolve_ffmpeg_binary() is not None
