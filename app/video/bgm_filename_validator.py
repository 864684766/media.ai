"""BGM 上传文件名校验。"""

from pathlib import Path

from app.core.bgm_constants import BGM_ALLOWED_EXTENSIONS


def validate_bgm_filename(filename: str) -> str:
    """校验并返回安全文件名。

    参数:
        filename: 原始上传文件名。

    返回:
        str:  basename 安全名。

    异常:
        ValueError: 扩展名不允许或文件名为空。
    """
    name = Path(filename or "").name.strip()
    if not name:
        raise ValueError("文件名不能为空")
    suffix = Path(name).suffix.lower()
    if suffix not in BGM_ALLOWED_EXTENSIONS:
        allowed = ", ".join(BGM_ALLOWED_EXTENSIONS)
        raise ValueError(f"不支持的 BGM 格式，允许: {allowed}")
    return name
