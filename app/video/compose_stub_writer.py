"""合成 Stub 文件写入。"""

from app.storage.local.artifact_writer import write_text_file
from app.video.compose_output_path_helper import (
    compose_output_path,
    compose_output_relative_uri,
)
from app.video.compose_timeline_builder import timeline_to_json


def write_compose_stub(project_id: str, timeline_payload: dict) -> str:
    """写出 timeline Stub JSON，返回相对 URI。

    参数:
        project_id: 项目 id。
        timeline_payload: 时间轴结构。

    返回:
        str: files API 相对路径。
    """
    path = compose_output_path(project_id)
    body = timeline_to_json(timeline_payload)
    write_text_file(path, body)
    return compose_output_relative_uri(project_id)
