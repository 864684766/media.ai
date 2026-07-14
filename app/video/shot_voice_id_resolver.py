"""镜头对白 voice_id 解析（V8）。

【职责】
    从 character_bible 取 shot 首个角色的 voice_id。

【何时调用】
    TTS 流水线生成对白轨前。
"""

from sqlalchemy.orm import Session

from app.core.audio_constants import DEFAULT_VOICE_ID
from app.models.postgres.shot_model import ShotModel
from app.storage.postgres.character_bible_repository import CharacterBibleRepository


def resolve_shot_voice_id(session: Session, shot: ShotModel) -> str:
    """解析镜头应使用的 voice_id。

    参数:
        session: DB Session。
        shot: 镜头 ORM。

    返回:
        str: voice_id 或默认值。
    """
    char_ids = shot.character_ids or []
    if not char_ids:
        return DEFAULT_VOICE_ID
    repo = CharacterBibleRepository(session)
    first_id = str(char_ids[0])
    row = repo.get_character(shot.project_id, first_id)
    if row is None or not row.voice_id:
        return DEFAULT_VOICE_ID
    return row.voice_id
