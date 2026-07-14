"""MCP render_shot 单镜渲染服务。"""

from sqlalchemy.orm import Session

from app.core.video_constants import ASSET_TYPE_CLIP, ASSET_TYPE_KEYFRAME, SHOT_STATUS_RENDERED, SHOT_STATUS_RENDERING
from app.storage.postgres.shot_asset_repository import ShotAssetRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.clip_render_dispatcher import dispatch_clip_render
from app.video.keyframe_render_dispatcher import dispatch_keyframe_render
from app.video.video_provider_config_reader import load_video_provider_config


def render_single_shot_for_mcp(session: Session, shot_id: str) -> dict:
    """渲染单镜并返回 clip / 关键帧 URI。

    参数:
        session: PG Session。
        shot_id: 镜头 id。

    返回:
        dict: MCP 工具出参。
    """
    shot = _load_shot_or_raise(session, shot_id)
    provider_cfg = load_video_provider_config()
    shot_repo = ShotRepository(session)
    asset_repo = ShotAssetRepository(session)
    shot_repo.update_shot_fields(shot.shot_id, SHOT_STATUS_RENDERING)
    frame_uri, _provider = dispatch_keyframe_render(shot, provider_cfg)
    clip_uri, last_frame, clip_provider, clip_cost = dispatch_clip_render(shot, provider_cfg)
    asset_repo.insert_asset(shot.shot_id, shot.project_id, ASSET_TYPE_KEYFRAME, frame_uri, provider=_provider)
    asset_repo.insert_asset(
        shot.shot_id, shot.project_id, ASSET_TYPE_CLIP, clip_uri, last_frame,
        provider=clip_provider, cost=clip_cost,
    )
    shot_repo.update_shot_fields(shot.shot_id, SHOT_STATUS_RENDERED, frame_uri)
    return {
        "shot_id": shot_id,
        "clip_uri": clip_uri,
        "keyframe_uri": frame_uri,
        "last_frame_uri": last_frame,
        "cost": clip_cost,
    }


def _load_shot_or_raise(session: Session, shot_id: str):
    """加载镜头或抛错。"""
    shot = ShotRepository(session).get_shot(shot_id)
    if shot is None:
        raise ValueError(f"镜头不存在: {shot_id}")
    return shot
