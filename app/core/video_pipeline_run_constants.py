"""视频子图运行态常量（阶段 D1）。"""

# 子图运行结果
PIPELINE_RUN_PENDING = "pending"
PIPELINE_RUN_COMPLETED = "completed"
PIPELINE_RUN_PAUSED = "paused"
PIPELINE_RUN_FAILED = "failed"

# 暂停原因
PAUSE_REASON_AWAITING_REVIEW = "awaiting_review"
PAUSE_REASON_NO_SHOTS = "no_shots"
PAUSE_REASON_COMPOSE_BLOCKED = "compose_blocked"
PAUSE_REASON_NO_VALIDATED_SHOTS = "no_validated_shots"
PAUSE_REASON_ALL_SHOTS_REJECTED = "all_shots_rejected"
PAUSE_REASON_AWAITING_BGM = "awaiting_bgm"

# 条件边分支名
BRANCH_PIPELINE_CONTINUE = "continue"
BRANCH_PIPELINE_PAUSE = "pause"

# API 路径后缀（挂于 VIDEO_ROUTE_PREFIX）
PIPELINE_RUN_ROUTE_SUFFIX = "/pipeline/run"
