"""Shot 业务 id 生成辅助。

【职责】
    为每条分镜生成全局唯一 shot_id（UUID 字符串）。
"""

import uuid


def new_shot_id() -> str:
    """生成新的 shot_id。

    返回:
        str: UUID 十六进制字符串（无连字符）。
    """
    return uuid.uuid4().hex
