"""真实音视频 E2E 断言。"""

from pathlib import Path

from app.video.video_assets_config_reader import load_video_assets_config
from app.video.video_compose_config_reader import load_video_compose_config


def assert_real_av_compose(compose_payload: dict) -> dict:
    """断言 compose 产出为 timeline.mp4 且文件存在。

    参数:
        compose_payload: compose API 响应 dict。

    返回:
        dict: 断言摘要。
    """
    uri = _resolve_output_uri(compose_payload)
    mp4_name = load_video_compose_config().output_mp4_filename
    is_mp4 = uri.endswith(mp4_name)
    exists = _file_exists(uri) if uri else False
    return {
        "output_uri": uri,
        "is_timeline_mp4": is_mp4,
        "file_exists": exists,
        "passed": is_mp4 and exists,
    }


def _resolve_output_uri(payload: dict) -> str:
    """从 compose 响应提取 output uri。"""
    output = payload.get("output") or {}
    if isinstance(output, dict) and output.get("uri"):
        return str(output["uri"])
    if payload.get("output_uri"):
        return str(payload["output_uri"])
    job = payload.get("job") or {}
    if isinstance(job, dict) and job.get("output_uri"):
        return str(job["output_uri"])
    return ""


def _file_exists(relative_uri: str) -> bool:
    """检查 assets_dir 下文件是否存在。"""
    root = Path(load_video_assets_config().assets_dir)
    path = (root / relative_uri).resolve()
    return path.is_file()
