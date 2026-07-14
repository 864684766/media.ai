"""知识库 HTTP 写入与分页常量（一处权威）。"""

# 上传来源默认标记
DEFAULT_KNOWLEDGE_SOURCE_UPLOAD = "upload"

# 粘贴文本来源标记
DEFAULT_KNOWLEDGE_SOURCE_PASTE = "paste"

# chunk 列表默认分页
DEFAULT_KNOWLEDGE_CHUNK_PAGE_SIZE = 20

# chunk 列表最大分页
MAX_KNOWLEDGE_CHUNK_PAGE_SIZE = 100

# 支持的导入扩展名（小写，含点）
SUPPORTED_INGEST_EXTENSIONS: tuple[str, ...] = (".txt", ".md", ".pdf", ".docx")

# 纯文本扩展名（无需额外解析库）
PLAIN_TEXT_INGEST_EXTENSIONS: tuple[str, ...] = (".txt", ".md")
