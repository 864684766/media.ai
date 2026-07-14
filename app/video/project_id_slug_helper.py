"""project_id slug 校验与生成。"""

import re

from app.core.video_project_constants import PROJECT_ID_MAX_LENGTH, PROJECT_ID_PATTERN


def is_valid_project_id(project_id: str) -> bool:
    """判断 project_id 是否为合法 slug。

    参数:
        project_id: 待校验字符串。

    返回:
        bool: 合法为 True。
    """
    if not project_id or len(project_id) > PROJECT_ID_MAX_LENGTH:
        return False
    return re.match(PROJECT_ID_PATTERN, project_id) is not None


def slug_from_title(title: str) -> str:
    """从标题生成默认 project_id slug。

    参数:
        title: 用户输入标题。

    返回:
        str: 小写 slug；空标题时返回 project。
    """
    raw = title.strip().lower()
    if not raw:
        return "project"
    cleaned = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return (cleaned or "project")[:PROJECT_ID_MAX_LENGTH]
