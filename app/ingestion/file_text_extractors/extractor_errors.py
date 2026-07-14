"""文件文本提取异常定义。"""


class UnsupportedFileExtensionError(Exception):
    """不支持的文件扩展名。"""

    def __init__(self, extension: str) -> None:
        """记录被拒绝的扩展名。"""
        super().__init__(extension)
        self.extension = extension
