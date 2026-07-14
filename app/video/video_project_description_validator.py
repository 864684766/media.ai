"""视频项目 description 字段校验（一处权威）。

【职责】
    规范化并校验 POST /video/projects 的 description 长度。

【何时调用】
    video_project_create_service 创建项目前。
"""

from app.core.video_project_constants import MAX_PROJECT_DESCRIPTION_LENGTH


class ProjectDescriptionTooLongError(Exception):
    """description 超过最大长度。"""


def normalize_project_description(raw: str) -> str:
    """裁剪首尾空白并校验长度。

    参数:
        raw: 请求体中的 description。

    返回:
        str: 规范化后的描述（可为空串）。

    异常:
        ProjectDescriptionTooLongError: 超出 MAX_PROJECT_DESCRIPTION_LENGTH。
    """
    text = raw.strip()
    if len(text) > MAX_PROJECT_DESCRIPTION_LENGTH:
        raise ProjectDescriptionTooLongError(MAX_PROJECT_DESCRIPTION_LENGTH)
    return text
