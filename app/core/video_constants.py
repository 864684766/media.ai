"""视频生产线跨层常量（一处权威）。

【职责】
    Shot 状态、默认状态等会被 API、Repository、测试共同引用的字面量。

【何时调用】
    入库、列表、状态迁移校验时 import，禁止在业务逻辑内联字符串。

【简例】
    status = DEFAULT_SHOT_STATUS  # → "draft"
"""

# Shot 状态：分镜已写入、未校验实体（V1 入库默认值）
SHOT_STATUS_DRAFT = "draft"
# Shot 状态：实体校验通过（V2 validate_entities 写入）
SHOT_STATUS_VALIDATED = "validated"
# Shot 状态：校验或生成失败
SHOT_STATUS_REJECTED = "rejected"
# Shot 状态：切片生成中（V3）
SHOT_STATUS_RENDERING = "rendering"
# Shot 状态：切片已落盘（V3 Stub）
SHOT_STATUS_RENDERED = "rendered"
# Shot 状态：连续性 QA 通过（V4）
SHOT_STATUS_QA_PASSED = "qa_passed"
# Shot 状态：连续性 QA 未过（V4，可重试）
SHOT_STATUS_QA_FAILED = "qa_failed"
# Shot 状态：QA 重试超限，等待人工（V4）
SHOT_STATUS_AWAITING_REVIEW = "awaiting_review"
# Shot 状态：已纳入时间轴合成（V5）
SHOT_STATUS_COMPOSED = "composed"

# Render Job 状态
JOB_STATUS_PENDING = "pending"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"

# Compose Job 状态（V5）
COMPOSE_JOB_STATUS_PENDING = "pending"
COMPOSE_JOB_STATUS_RUNNING = "running"
COMPOSE_JOB_STATUS_COMPLETED = "completed"
COMPOSE_JOB_STATUS_FAILED = "failed"

# shot_assets.asset_type
ASSET_TYPE_KEYFRAME = "keyframe"
ASSET_TYPE_CLIP = "clip"

# V1 新镜头默认状态
DEFAULT_SHOT_STATUS = SHOT_STATUS_DRAFT

# validate 失败原因前缀（API failures.reasons 与测试断言共用）
REASON_MISSING_CHARACTER = "missing_character"
REASON_MISSING_SCENE = "missing_scene"
REASON_MISSING_PROP = "missing_prop"

# V4 连续性 QA 失败原因前缀
REASON_MISSING_TRANSITION = "missing_transition"
REASON_MISSING_KEYFRAME = "missing_keyframe"
REASON_INVALID_DURATION = "invalid_duration"
REASON_PROP_DROPPED = "prop_dropped"

# V5 合成：无 qa_passed 镜头时拒绝
REASON_NO_QA_PASSED_SHOTS = "no_qa_passed_shots"

# V5 合成产物默认文件名（可被 app.yaml 覆盖）
DEFAULT_COMPOSE_OUTPUT_FILENAME = "timeline.stub.json"

# V7 切片文件名
CLIP_FILENAME_STUB = "clip.stub.txt"
CLIP_FILENAME_MP4 = "clip.mp4"

# V7 Provider id（引用 video_provider_constants 别名，跨层测试用）
VIDEO_PROVIDER_STUB = "stub"
VIDEO_PROVIDER_LOCAL_FFMPEG = "local_ffmpeg"

# V6 HITL review 动作
REVIEW_ACTION_APPROVE = "approve"
REVIEW_ACTION_REJECT = "reject"

# V6 HITL 审核阶段（与 video.review 配置对应）
REVIEW_STAGE_QA_OVERFLOW = "qa_overflow"
REVIEW_STAGE_KEYFRAME = "keyframe"
REVIEW_STAGE_STORYBOARD = "storyboard"

# V6 流水线步骤 id（media-web 进度展示）
PIPELINE_STEP_STORYBOARD = "storyboard"
PIPELINE_STEP_VALIDATE = "validate"
PIPELINE_STEP_RENDER = "render"
PIPELINE_STEP_QA = "qa"
PIPELINE_STEP_COMPOSE = "compose"

# 视频 API 路由前缀（完整路径 /api/v1/video，全局前缀在 core/constants）
VIDEO_ROUTE_PREFIX = "/video"
