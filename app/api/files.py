"""静态产物文件访问 API（视频资产等）。"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.api.api_constants import FILES_ROUTE_PREFIX
from app.video.video_asset_path_helper import shot_asset_dir
from app.video.video_assets_config_reader import load_video_assets_config

router = APIRouter(prefix=FILES_ROUTE_PREFIX, tags=["files"])


def _resolve_video_file(relative_path: str) -> Path:
    """解析视频相对路径并防目录穿越。

    参数:
        relative_path: 形如 project_id/shot_id/file.ext

    异常:
        HTTPException: 非法路径或文件不存在。
    """
    root = Path(load_video_assets_config().assets_dir).resolve()
    target = (root / relative_path).resolve()
    if not str(target).startswith(str(root)):
        raise HTTPException(status_code=400, detail="非法路径")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return target


def _media_type_for_filename(filename: str) -> str | None:
    """按扩展名返回 Content-Type。"""
    lower = filename.lower()
    if lower.endswith(".json"):
        return "application/json"
    if lower.endswith(".mp4"):
        return "video/mp4"
    if lower.endswith(".svg"):
        return "image/svg+xml"
    if lower.endswith(".wav"):
        return "audio/wav"
    if lower.endswith(".srt"):
        return "text/plain"
    return None


@router.get(
    "/video/{project_id}/audio/{shot_id}/{filename}",
    summary="打开/下载对白音频",
)
def get_audio_asset_file(
    project_id: str,
    shot_id: str,
    filename: str,
    disposition: str = Query(default="inline"),
) -> FileResponse:
    """V8 对白 WAV inline/attachment。"""
    relative = f"{project_id}/audio/{shot_id}/{filename}"
    path = _resolve_video_file(relative)
    mode = "inline" if disposition == "inline" else "attachment"
    return FileResponse(
        path,
        filename=filename,
        media_type=_media_type_for_filename(filename),
        content_disposition_type=mode,
    )


@router.get("/video/{project_id}/{shot_id}/{filename}", summary="打开/下载视频资产")
def get_video_asset_file(
    project_id: str,
    shot_id: str,
    filename: str,
    disposition: str = Query(default="inline"),
) -> FileResponse:
    """disposition=inline 浏览器打开；attachment 下载。"""
    relative = f"{project_id}/{shot_id}/{filename}"
    _ = shot_asset_dir(project_id, shot_id)
    path = _resolve_video_file(relative)
    mode = "inline" if disposition == "inline" else "attachment"
    return FileResponse(
        path,
        filename=filename,
        media_type=_media_type_for_filename(filename),
        content_disposition_type=mode,
    )


@router.get(
    "/video/{project_id}/compose/{filename}",
    summary="打开/下载合成成片 Stub",
)
def get_compose_output_file(
    project_id: str,
    filename: str,
    disposition: str = Query(default="inline"),
) -> FileResponse:
    """V5 时间轴 JSON Stub 的 inline/attachment 访问。"""
    relative = f"{project_id}/compose/{filename}"
    path = _resolve_video_file(relative)
    mode = "inline" if disposition == "inline" else "attachment"
    media = _media_type_for_filename(filename)
    return FileResponse(
        path,
        filename=filename,
        media_type=media,
        content_disposition_type=mode,
    )
