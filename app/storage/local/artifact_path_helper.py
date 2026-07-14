"""本地 artifact 路径辅助。"""

from pathlib import Path

from app.core.artifact_constants import DEFAULT_NOVEL_ARTIFACT_DIR, NOVEL_ARTIFACT_EXT
from app.storage.local.artifact_config_reader import load_artifact_config


def novel_artifact_path(conversation_id: str, message_id: int) -> Path:
    """计算小说 TXT 落盘路径。

    参数:
        conversation_id: 会话 id。
        message_id: 消息自增 id。

    返回:
        Path: 绝对或相对路径对象。
    """
    root = Path(load_artifact_config().novel_dir)
    return root / conversation_id / f"{message_id}{NOVEL_ARTIFACT_EXT}"
