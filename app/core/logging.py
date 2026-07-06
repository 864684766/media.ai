"""日志辅助方法。

单独文件承载日志相关逻辑，保证 core 模块的单一职责。
"""

import logging
import sys

from app.core.config import settings


def _build_stream_handler() -> logging.StreamHandler:
    """构建标准输出日志处理器。

    返回:
        logging.StreamHandler: 配置好日志格式的控制台处理器。
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def setup_logging() -> logging.Logger:
    """初始化应用日志。

    返回:
        logging.Logger: 应用根日志器。
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger = logging.getLogger(settings.app_name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(_build_stream_handler())
    return logger


logger = setup_logging()
