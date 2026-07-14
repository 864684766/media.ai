"""V3 Stub：关键帧与切片占位文件生成。"""

from pathlib import Path

from app.models.postgres.shot_model import ShotModel
from app.storage.local.artifact_writer import write_text_file
from app.video.video_asset_path_helper import clip_file_path, keyframe_file_path


def write_keyframe_stub(shot: ShotModel) -> str:
    """写出 SVG 关键帧 Stub，返回相对 URI 片段。

    参数:
        shot: 镜头 ORM。

    返回:
        str: 供 API 访问的相对路径（project/shot/file）。
    """
    path = keyframe_file_path(shot.project_id, shot.shot_id)
    svg = _build_keyframe_svg(shot)
    write_text_file(path, svg)
    return _relative_uri(shot.project_id, shot.shot_id, path.name)


def write_clip_stub(shot: ShotModel) -> tuple[str, str]:
    """写出切片 Stub 与伪 last_frame 路径。

    返回:
        tuple[str, str]: (clip_uri, last_frame_uri)。
    """
    clip_path = clip_file_path(shot.project_id, shot.shot_id)
    body = f"V3 Stub clip for shot {shot.shot_no}\naction: {shot.action}\n"
    write_text_file(clip_path, body)
    frame_uri = write_keyframe_stub(shot)
    clip_uri = _relative_uri(shot.project_id, shot.shot_id, clip_path.name)
    return clip_uri, frame_uri


def _relative_uri(project_id: str, shot_id: str, filename: str) -> str:
    """拼接相对 URI（files API 使用）。"""
    return f"{project_id}/{shot_id}/{filename}"


def _build_keyframe_svg(shot: ShotModel) -> str:
    """生成简易 SVG 占位图内容。"""
    title = shot.action or shot.shot_no
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">'
        f'<rect width="100%" height="100%" fill="#e0f2fe"/>'
        f'<text x="32" y="48" font-size="20">Shot {shot.shot_no}</text>'
        f'<text x="32" y="80" font-size="14">{title}</text></svg>'
    )
