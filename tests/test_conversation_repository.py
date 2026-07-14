"""ConversationRepository 单元测试（SQLite 内存库）。"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_metadata import create_all_tables


def test_create_conversation() -> None:
    """创建会话后应能按 id 取回。"""
    session = _open_test_session()
    repository = ConversationRepository(session)
    repository.create_conversation("c-1", project_id="p-1")
    conversation = repository.get_conversation("c-1")
    assert conversation is not None
    assert conversation.project_id == "p-1"


def test_append_and_list_messages() -> None:
    """追加 user/assistant 消息后，应按顺序读回。"""
    session = _open_test_session()
    repository = ConversationRepository(session)
    repository.create_conversation("c-2")
    repository.append_message("c-2", pc.MESSAGE_ROLE_USER, "你好")
    repository.append_message("c-2", pc.MESSAGE_ROLE_ASSISTANT, "你好，我在")
    messages = repository.list_messages("c-2")
    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["你好", "你好，我在"]


def _open_test_session() -> Session:
    """创建 SQLite 内存库 Session。"""
    engine = _create_test_engine()
    create_all_tables(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return factory()


def _create_test_engine() -> Engine:
    """创建测试用 SQLAlchemy Engine。"""
    return create_engine("sqlite+pysqlite:///:memory:")
