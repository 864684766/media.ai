"""创作类型常量（小说 / 视频分流）。

【职责】
    定义 creation_type 取值与各类别默认 Skill 池，供 ChatRequest 与 Skill 匹配共用。
"""

# ChatRequest.creation_type 合法取值
CREATION_TYPE_NOVEL = "novel"
CREATION_TYPE_VIDEO = "video"

# 小说类默认 Skill（自动匹配池）
NOVEL_SKILL_IDS = frozenset({"novel-writing"})
DEFAULT_NOVEL_SKILL_ID = "novel-writing"

# 视频类默认 Skill 池（顺序：导演优先，其次分镜）
VIDEO_SKILL_IDS = frozenset({"director", "storyboard"})
DEFAULT_VIDEO_SKILL_ID = "director"
VIDEO_SKILL_PRIORITY = ("director", "storyboard")

# 全部合法 creation_type
ALLOWED_CREATION_TYPES = frozenset({CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO})
