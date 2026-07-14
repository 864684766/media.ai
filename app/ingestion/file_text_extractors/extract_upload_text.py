"""上传文件 → 纯文本统一入口。"""

from app.core.knowledge_constants import (
    PLAIN_TEXT_INGEST_EXTENSIONS,
    SUPPORTED_INGEST_EXTENSIONS,
)
from app.ingestion.file_text_extractors.docx_text_extractor import extract_docx_text
from app.ingestion.file_text_extractors.extension_helper import resolve_extension
from app.ingestion.file_text_extractors.extractor_errors import UnsupportedFileExtensionError
from app.ingestion.file_text_extractors.pdf_text_extractor import extract_pdf_text
from app.ingestion.file_text_extractors.plain_text_extractor import extract_plain_text

_EXTENSION_EXTRACTORS = {
    ".pdf": extract_pdf_text,
    ".docx": extract_docx_text,
}


def extract_text_from_upload(filename: str, data: bytes) -> str:
    """按扩展名提取上传文件正文。

    参数:
        filename: 原始文件名。
        data: 文件字节。

    返回:
        str: 提取后的纯文本。

    异常:
        UnsupportedFileExtensionError: 扩展名不在支持列表。
    """
    extension = resolve_extension(filename)
    _ensure_supported(extension)
    if extension in PLAIN_TEXT_INGEST_EXTENSIONS:
        return extract_plain_text(data)
    extractor = _EXTENSION_EXTRACTORS[extension]
    return extractor(data)


def list_rejected_extensions(filenames: list[str]) -> list[str]:
    """过滤出不支持的扩展名列表。"""
    rejected: list[str] = []
    for name in filenames:
        extension = resolve_extension(name)
        if extension and extension not in SUPPORTED_INGEST_EXTENSIONS:
            rejected.append(extension)
    return sorted(set(rejected))


def _ensure_supported(extension: str) -> None:
    """校验扩展名是否受支持。"""
    if extension not in SUPPORTED_INGEST_EXTENSIONS:
        raise UnsupportedFileExtensionError(extension)
