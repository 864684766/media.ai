"""PDF 文本提取（pypdf）。"""

from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(data: bytes) -> str:
    """从 PDF 字节流提取纯文本。

    参数:
        data: PDF 文件字节。

    返回:
        str: 各页文本拼接结果。
    """
    reader = PdfReader(BytesIO(data))
    pages = [_page_text(page.extract_text()) for page in reader.pages]
    return "\n".join(part for part in pages if part)


def _page_text(raw: str | None) -> str:
    """规范化单页提取结果。"""
    return (raw or "").strip()
