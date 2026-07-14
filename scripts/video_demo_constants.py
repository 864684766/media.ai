"""视频 E2E 演示常量。"""

from pathlib import Path

# 默认演示项目 id
DEFAULT_DEMO_PROJECT_ID = "demo-e2e"

# fixtures 路径（相对 scripts 目录）
SCRIPTS_DIR = Path(__file__).resolve().parent
FIXTURE_STORYBOARD = SCRIPTS_DIR / "fixtures" / "demo-storyboard.json"
FIXTURE_BIBLE = SCRIPTS_DIR / "fixtures" / "demo-bible.json"

# 演示模式：逐步 API（legacy）或 G2+管线（pipeline）
DEMO_MODE_STEP = "step"
DEMO_MODE_PIPELINE = "pipeline"

# 管线执行：同步子图或异步 Job（脚本内同步 execute）
PIPELINE_MODE_SYNC = "sync"
PIPELINE_MODE_ASYNC = "async"

# 音视频模式：stub 仅验收链路；real 断言 timeline.mp4
AV_MODE_STUB = "stub"
AV_MODE_REAL = "real"
