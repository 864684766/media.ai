"""字幕烧录开关与结果标记。"""

from app.video.audio_output_path_helper import subtitle_srt_path
from app.video.video_audio_config_reader import load_video_audio_config

MP4_SUFFIX = ".mp4"


def should_burn_subtitles_for_project(project_id: str, output_uri: str) -> bool:
    """是否应在合成后烧录字幕。

    参数:
        project_id: 项目 id。
        output_uri: 合成产物相对 URI。

    返回:
        bool: 配置开启、产物为 mp4 且 SRT 存在时为 True。
    """
    cfg = load_video_audio_config()
    if not cfg.compose_burn_subtitles:
        return False
    if not output_uri.lower().endswith(MP4_SUFFIX):
        return False
    return subtitle_srt_path(project_id).is_file()


def resolve_subtitles_burned_flag(project_id: str, output_uri: str) -> bool:
    """推断成片是否已执行字幕烧录（与 should 条件一致）。

    参数:
        project_id: 项目 id。
        output_uri: 合成产物 URI。

    返回:
        bool: 供 API subtitles_burned 字段。
    """
    return should_burn_subtitles_for_project(project_id, output_uri)
