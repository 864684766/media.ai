"""策划→分镜（阶段 G2）常量。"""

from app.core.creation_type_constants import CREATION_TYPE_VIDEO

# 分镜 Skill 权威 id（与 skills/storyboard 对齐）
PLAN_STORYBOARD_SKILL_ID = "storyboard"

# REST 子路径（挂于 CREATIVE_ROUTE_PREFIX）
PLAN_STORYBOARD_ROUTE_SUFFIX = "/storyboard"

# 用户 prompt 引导语
PLAN_STORYBOARD_PROMPT_INTRO = (
    "请根据以下已确认的视频策划方案，输出完整分镜 JSON 数组。"
    "必须用 ```json 代码块包裹；字段与 storyboard Skill 规范一致。"
)

# 错误文案
ERR_PLAN_NOT_FOUND = "大纲不存在"
ERR_PLAN_NOT_APPROVED = "大纲尚未确认，无法生成分镜"
ERR_PLAN_NOT_VIDEO = "仅视频类大纲支持一键生成分镜"
ERR_PROJECT_ID_REQUIRED = "请指定 project_id（请求体或大纲关联项目）"
ERR_STORYBOARD_PARSE_FAILED = "分镜 JSON 解析失败"

# 创作类型引用
PLAN_STORYBOARD_CREATION_TYPE = CREATION_TYPE_VIDEO

# 模板拆镜默认景别
DEFAULT_TEMPLATE_SHOT_SIZE = "中景"
