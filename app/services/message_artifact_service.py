"""助手消息 TXT 产物服务（小说导出）。"""

from pathlib import Path

from app.storage.local.artifact_path_helper import novel_artifact_path
from app.storage.local.artifact_writer import write_text_file
from app.storage.postgres.conversation_repository import ConversationRepository


def save_assistant_txt_artifact(
    repository: ConversationRepository,
    conversation_id: str,
    message_id: int,
) -> Path | None:
    """将助手消息正文写入 TXT 文件。

    参数:
        repository: 会话 Repository。
        conversation_id: 会话 id。
        message_id: 助手消息 id。

    返回:
        Path | None: 写入路径；消息不存在时 None。
    """
    message = repository.get_message(conversation_id, message_id)
    if message is None:
        return None
    target = novel_artifact_path(conversation_id, message_id)
    return write_text_file(target, message.content)


def resolve_assistant_txt_path(conversation_id: str, message_id: int) -> Path:
    """解析 TXT 路径（不保证文件存在）。"""
    return novel_artifact_path(conversation_id, message_id)
