"""DOCX 文本提取（python-docx）。"""

from io import BytesIO

from docx import Document


def extract_docx_text(data: bytes) -> str:
    """从 DOCX 字节流提取段落文本。

    参数:
        data: DOCX 文件字节。

    返回:
        str: 段落以换行拼接。
    """
    document = Document(BytesIO(data))
    lines = [paragraph.text.strip() for paragraph in document.paragraphs]
    return "\n".join(line for line in lines if line)
