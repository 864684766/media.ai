"""创作产物（artifact）跨层常量。

【职责】
    小说 TXT、视频资产等可下载文件的 MIME、后缀与 API 路径片段。
"""

# 小说助手消息 TXT 后缀
NOVEL_ARTIFACT_EXT = ".txt"
# 小说 TXT MIME（浏览器打开/下载）
NOVEL_ARTIFACT_MIME = "text/plain; charset=utf-8"

# artifacts API 路径片段（挂在 /conversations/{id}/messages/{mid}/ 下）
ARTIFACT_ROUTE_SEGMENT = "artifact"
ARTIFACT_DOWNLOAD_SEGMENT = "artifact/download"

# 默认小说产物根目录（可被 app.yaml artifacts.novel_dir 覆盖）
DEFAULT_NOVEL_ARTIFACT_DIR = "data/artifacts/novel"
