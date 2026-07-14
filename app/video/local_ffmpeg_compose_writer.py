"""local_ffmpeg 时间轴 mp4 合成（V7）。

【职责】
    用 concat demuxer 将多镜 clip.mp4 拼接为 timeline.mp4。

【何时调用】
    compose_output_dispatcher 在 active.compose=local_ffmpeg 时。
"""

import subprocess
import tempfile
from pathlib import Path

from app.video.compose_bgm_mix_step import maybe_mix_bgm_into_output
from app.video.compose_subtitle_burn_step import maybe_burn_subtitles_into_output
from app.video.compose_timeline_mux_helper import extract_mux_inputs, has_dialogue_tracks
from app.video.dialogue_timeline_wav_builder import build_timeline_dialogue_wav
from app.video.ffmpeg_binary_resolver import resolve_ffmpeg_binary
from app.video.local_ffmpeg_audio_muxer import mux_video_with_audio
from app.video.video_assets_config_reader import load_video_assets_config
from app.video.video_audio_config_reader import load_video_audio_config
from app.video.video_compose_config_reader import load_video_compose_config


def write_local_ffmpeg_compose(
    project_id: str,
    clip_relative_uris: list[str],
    timeline_payload: dict | None = None,
) -> str:
    """拼接 clip 列表为 timeline.mp4，可选混入对白轨。

    参数:
        project_id: 项目 id。
        clip_relative_uris: 各镜 clip 相对 URI。
        timeline_payload: 时间轴 JSON（含 clips / audio_tracks）。

    返回:
        str: compose 相对 URI（project/compose/timeline.mp4）。
    """
    binary = resolve_ffmpeg_binary()
    if binary is None:
        raise RuntimeError("ffmpeg not available")
    root = Path(load_video_assets_config().assets_dir)
    abs_clips = [_resolve_clip(root, uri) for uri in clip_relative_uris]
    output = _compose_output_path(project_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    if _should_mux_audio(timeline_payload):
        _compose_with_mux(binary, root, project_id, abs_clips, output, timeline_payload)
    else:
        _concat_mp4(binary, abs_clips, output)
    relative = f"{project_id}/compose/{load_video_compose_config().output_mp4_filename}"
    maybe_burn_subtitles_into_output(binary, project_id, output, relative)
    filename = load_video_compose_config().output_mp4_filename
    return f"{project_id}/compose/{filename}"


def _should_mux_audio(timeline_payload: dict | None) -> bool:
    """是否启用音画混轨。"""
    cfg = load_video_audio_config()
    return cfg.compose_mux_audio and has_dialogue_tracks(timeline_payload)


def _compose_with_mux(
    binary: str,
    root: Path,
    project_id: str,
    clips: list[Path],
    output: Path,
    timeline_payload: dict | None,
) -> None:
    """先 concat 视频，再混对白轨。"""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_only = Path(tmp.name)
    try:
        _concat_mp4(binary, clips, video_only)
        clips_meta, tracks = extract_mux_inputs(timeline_payload)
        dialogue_wav = output.parent / "dialogue_timeline.wav"
        if build_timeline_dialogue_wav(clips_meta, tracks, root, dialogue_wav):
            mux_video_with_audio(binary, video_only, dialogue_wav, output)
        else:
            video_only.replace(output)
        maybe_mix_bgm_into_output(binary, project_id, output, timeline_payload)
    finally:
        video_only.unlink(missing_ok=True)


def _resolve_clip(root: Path, relative_uri: str) -> Path:
    """将相对 URI 解析为绝对路径并校验后缀。"""
    path = (root / relative_uri).resolve()
    if path.suffix.lower() != ".mp4":
        raise RuntimeError(f"clip not mp4: {relative_uri}")
    if not path.is_file():
        raise RuntimeError(f"clip missing: {relative_uri}")
    return path


def _compose_output_path(project_id: str) -> Path:
    """成片 mp4 绝对路径。"""
    root = Path(load_video_assets_config().assets_dir)
    filename = load_video_compose_config().output_mp4_filename
    return root / project_id / "compose" / filename


def _concat_mp4(binary: str, clips: list[Path], output: Path) -> None:
    """执行 ffmpeg concat。"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        for clip in clips:
            safe = str(clip).replace("\\", "/").replace("'", "'\\''")
            tmp.write(f"file '{safe}'\n")
        list_path = tmp.name
    cmd = [binary, "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", str(output)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    Path(list_path).unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg concat failed")
