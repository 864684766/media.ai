"""合成后可选字幕烧录步骤。"""

import tempfile
from pathlib import Path

from app.video.audio_output_path_helper import subtitle_srt_path
from app.video.local_ffmpeg_subtitle_burner import burn_subtitles_into_mp4
from app.video.subtitle_burn_eligibility import should_burn_subtitles_for_project


def maybe_burn_subtitles_into_output(
    binary: str,
    project_id: str,
    output_path: Path,
    output_uri: str,
) -> bool:
    """若满足条件则将 SRT 烧录进成片 mp4。

    参数:
        binary: ffmpeg 路径。
        project_id: 项目 id。
        output_path: 成片绝对路径。
        output_uri: 相对 URI（用于判定 mp4）。

    返回:
        bool: 实际执行烧录时为 True。
    """
    if not should_burn_subtitles_for_project(project_id, output_uri):
        return False
    srt = subtitle_srt_path(project_id)
    _burn_inplace(binary, output_path, srt)
    return True


def _burn_inplace(binary: str, output_path: Path, srt_path: Path) -> None:
    """写入临时文件后替换原成片。"""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        burned = Path(tmp.name)
    try:
        burn_subtitles_into_mp4(binary, output_path, srt_path, burned)
        burned.replace(output_path)
    finally:
        burned.unlink(missing_ok=True)
