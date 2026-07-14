"""audio 节点：合成前 BGM 暂停判定。"""

from app.video.video_audio_config_reader import load_video_audio_config


def should_pause_for_bgm_before_compose() -> bool:
    """是否在对白完成后暂停，等待用户上传 BGM。"""
    return load_video_audio_config().bgm_pause_before_compose
