"""PostgreSQL 会话 Repository。

【职责】
    封装 conversations / messages 表的基础读写，供 load_history / save_messages 使用。

【为什么叫 Repository】
    API / LangGraph 不直接写 SQLAlchemy 查询，而是通过 Repository 表达业务动作：
    创建会话、追加消息、读取历史。
"""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.postgres.conversation_model import ConversationModel
from app.models.postgres.message_model import MessageModel
from app.models.postgres.time_helper import utc_now


class ConversationRepository:
    """会话与消息持久化。

    参数说明:
        session: 由 postgres_session_scope 提供的 SQLAlchemy Session。
    """

    def __init__(self, session: Session) -> None:
        """绑定数据库 Session。

        参数:
            session: 当前请求或任务使用的 Session。
        """
        self._session = session

    @property
    def db_session(self) -> Session:
        """暴露底层 Session（澄清等扩展表写入用）。"""
        return self._session

    def create_conversation(
        self,
        conversation_id: str,
        project_id: str | None = None,
        creation_type: str | None = None,
    ) -> ConversationModel:
        """创建会话。

        参数:
            conversation_id: 业务会话 id。
            project_id: 可选项目 id。
            creation_type: 创作类型 novel | video。

        返回:
            ConversationModel: 已创建会话。
        """
        conversation = ConversationModel(
            id=conversation_id,
            project_id=project_id,
            creation_type=creation_type,
        )
        self._session.add(conversation)
        self._session.commit()
        self._session.refresh(conversation)
        return conversation

    def set_creation_type(self, conversation_id: str, creation_type: str) -> None:
        """写入会话创作类型（仅当尚未设置时调用）。

        参数:
            conversation_id: 会话 id。
            creation_type: novel | video。
        """
        conversation = self.get_conversation(conversation_id)
        if conversation is None or conversation.creation_type:
            return
        conversation.creation_type = creation_type
        conversation.updated_at = utc_now()
        self._session.commit()

    def get_conversation(self, conversation_id: str) -> ConversationModel | None:
        """按 id 获取会话。

        参数:
            conversation_id: 会话 id。

        返回:
            ConversationModel | None: 找到则返回，否则 None。
        """
        return self._session.get(ConversationModel, conversation_id)

    def append_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> MessageModel:
        """向会话追加一条消息。

        参数:
            conversation_id: 会话 id。
            role: user / assistant / system。
            content: 消息正文。

        返回:
            MessageModel: 已保存消息。
        """
        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self._session.add(message)
        self._touch_conversation(conversation_id)
        self._session.commit()
        self._session.refresh(message)
        return message

    def list_messages(
        self,
        conversation_id: str,
        retention_days: int | None = None,
    ) -> list[MessageModel]:
        """按创建顺序读取会话消息。

        参数:
            conversation_id: 会话 id。
            retention_days: 可选保留天数（config/app.yaml history.retention_days）；
                传入时只返回该天数内创建的消息，超期消息视为已归档。

        返回:
            list[MessageModel]: 消息列表。
        """
        query = self._session.query(MessageModel)
        query = query.filter(MessageModel.conversation_id == conversation_id)
        if retention_days is not None:
            cutoff = utc_now() - timedelta(days=retention_days)
            query = query.filter(MessageModel.created_at >= cutoff)
        return query.order_by(MessageModel.id.asc()).all()

    def get_message(
        self,
        conversation_id: str,
        message_id: int,
    ) -> MessageModel | None:
        """按会话与消息 id 读取单条消息。

        参数:
            conversation_id: 会话 id。
            message_id: 消息自增 id。

        返回:
            MessageModel | None: 找到则返回。
        """
        message = self._session.get(MessageModel, message_id)
        if message is None or message.conversation_id != conversation_id:
            return None
        return message

    def _touch_conversation(self, conversation_id: str) -> None:
        """更新会话 updated_at。"""
        conversation = self.get_conversation(conversation_id)
        if conversation is not None:
            conversation.updated_at = utc_now()
