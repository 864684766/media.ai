"""PostgreSQL ORM 模型导出。

【职责】
    统一导入 Base 与全部表模型，方便测试或 migrations 使用。
    新增表模型后必须在此导出，create_all_tables 才能建到它。
"""

from app.models.postgres.base import Base
from app.models.postgres.chunk_model import ChunkModel
from app.models.postgres.conversation_model import ConversationModel
from app.models.postgres.document_model import DocumentModel
from app.models.postgres.message_model import MessageModel
from app.models.postgres.shot_model import ShotModel
from app.models.postgres.character_bible_model import CharacterBibleModel
from app.models.postgres.compose_job_model import ComposeJobModel
from app.models.postgres.scene_lock_model import SceneLockModel
from app.models.postgres.prop_inventory_model import PropInventoryModel
from app.models.postgres.shot_asset_model import ShotAssetModel
from app.models.postgres.video_render_job_model import VideoRenderJobModel
from app.models.postgres.video_project_model import VideoProjectModel
from app.models.postgres.audio_asset_model import AudioAssetModel
from app.models.postgres.clarification_session_model import ClarificationSessionModel
from app.models.postgres.creative_plan_model import CreativePlanModel

__all__ = [
    "Base",
    "ChunkModel",
    "ConversationModel",
    "DocumentModel",
    "MessageModel",
    "ShotModel",
    "CharacterBibleModel",
    "ComposeJobModel",
    "SceneLockModel",
    "PropInventoryModel",
    "ShotAssetModel",
    "VideoRenderJobModel",
    "VideoProjectModel",
    "AudioAssetModel",
    "ClarificationSessionModel",
    "CreativePlanModel",
]
