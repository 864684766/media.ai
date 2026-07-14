"""纯文本字节解码。"""


def extract_plain_text(data: bytes) -> str:
    """将 txt/md 字节解码为 UTF-8 文本。

    参数:
        data: 文件原始字节。

    返回:
        str: 解码后的正文。
    """
    return data.decode("utf-8")
