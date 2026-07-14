"""ORM 模型注册表（create_all_tables 与 Alembic 共用）。

【职责】
    副作用 import 全部表模型，确保 Base.metadata 完整。

【何时调用】
    postgres_metadata.create_all_tables、alembic/env.py 启动时。
"""

from app.models.postgres import (  # noqa: F401
    AudioAssetModel,
    Base,
    CharacterBibleModel,
    ChunkModel,
    ClarificationSessionModel,
    ComposeJobModel,
    ConversationModel,
    DocumentModel,
    MessageModel,
    PropInventoryModel,
    SceneLockModel,
    ShotAssetModel,
    ShotModel,
    VideoProjectModel,
    VideoRenderJobModel,
)
from app.models.postgres.video_pipeline_job_model import VideoPipelineJobModel  # noqa: F401
from app.models.postgres.creative_plan_model import CreativePlanModel  # noqa: F401


def register_all_orm_models() -> None:
    """注册全部 ORM 表到 Base.metadata（无返回值，仅副作用）。"""
    return None
