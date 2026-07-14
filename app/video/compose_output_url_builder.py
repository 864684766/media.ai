"""合成产物 open/download URL 构建。"""


def build_compose_open_url(relative_uri: str) -> str:
    """浏览器 inline 打开成片 Stub。"""
    base = f"/api/v1/files/video/{relative_uri}"
    return f"{base}?disposition=inline"


def build_compose_download_url(relative_uri: str) -> str:
    """attachment 下载成片 Stub。"""
    base = f"/api/v1/files/video/{relative_uri}"
    return f"{base}?disposition=attachment"
