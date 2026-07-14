"""闲置配置项接入测试（history.retention_days / skills.auto_discover / web_search）。

【覆盖点】
    1. retention_days：超期消息不再被 list_messages 返回。
    2. auto_discover=false：未显式指定 skill_id 时不自动匹配。
    3. web_search 配置读取：max_results 生效与非法值回落。
"""

from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.postgres.time_helper import utc_now
from app.retrieval.web_search_settings_reader import load_web_search_settings
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.history_settings_reader import load_history_retention_days
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def repository() -> ConversationRepository:
    """SQLite 内存库 Repository。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as session:
        yield ConversationRepository(session)


def test_retention_days_filters_old_messages(repository: ConversationRepository) -> None:
    """超过保留期的消息应被过滤，期内消息保留。"""
    repository.create_conversation("conv-1")
    old_message = repository.append_message("conv-1", "user", "很久以前的消息")
    old_message.created_at = utc_now() - timedelta(days=100)
    repository.append_message("conv-1", "user", "最近的消息")
    messages = repository.list_messages("conv-1", retention_days=90)
    assert [message.content for message in messages] == ["最近的消息"]


def test_retention_days_reader_defaults() -> None:
    """history 段缺失或非法时应回落 90 天。"""
    assert load_history_retention_days({}) == 90
    assert load_history_retention_days({"history": {"retention_days": -1}}) == 90
    assert load_history_retention_days({"history": {"retention_days": 30}}) == 30


def test_auto_discover_disabled_skips_matching(monkeypatch: pytest.MonkeyPatch) -> None:
    """auto_discover=false 且未指定 skill_id 时应返回空 SkillContext。"""
    from app.skills import registry

    monkeypatch.setattr(registry, "is_auto_discover_enabled", lambda: False)
    context = registry.load_skill_context(skill_id=None, user_message="续写打斗")
    assert context.system_prompt == ""


def test_web_search_settings_reader() -> None:
    """web_search 配置应正确读取，非法 max_results 回落默认值。"""
    settings = load_web_search_settings({"web_search": {"provider": "tavily", "max_results": 3}})
    assert settings["max_results"] == 3
    fallback = load_web_search_settings({"web_search": {"max_results": 0}})
    assert fallback["max_results"] == 5
