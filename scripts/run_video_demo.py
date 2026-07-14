"""视频生产线 E2E 演示脚本（阶段 C + E4）。

【用途】
    step 模式：建项目 → 分镜 → bible → 校验 → 渲染 → QA → 音频 → 合成。
    pipeline 模式：G2 策划→分镜 → bible → 校验 → D1/D3 一键管线 → G3 字幕字段断言。

【运行】
    poetry run python scripts/run_video_demo.py
    poetry run python scripts/run_video_demo.py --demo-mode pipeline
    poetry run python scripts/run_video_demo.py --demo-mode pipeline --pipeline-mode async

【前置】
    1. .env 配置 DATABASE_URL
    2. poetry run alembic upgrade head  或 init_postgres_tables.py
    3. 可选：ffmpeg + video.providers.active 设为 local_ffmpeg
"""

import argparse
import json

from app.services.compose_job_service import ComposeBlockedError
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured
from video_demo_av_assert import assert_real_av_compose
from video_demo_constants import (
    AV_MODE_REAL,
    AV_MODE_STUB,
    DEFAULT_DEMO_PROJECT_ID,
    DEMO_MODE_PIPELINE,
    DEMO_MODE_STEP,
    FIXTURE_BIBLE,
    FIXTURE_STORYBOARD,
    PIPELINE_MODE_ASYNC,
    PIPELINE_MODE_SYNC,
)
from video_demo_g2_runner import run_demo_plan_storyboard
from video_demo_g3_assert import assert_subtitles_burned_field
from video_demo_pipeline_runner import run_demo_pipeline
from video_demo_step_runner import (
    ensure_demo_project,
    run_demo_audio,
    run_demo_bible,
    run_demo_compose,
    run_demo_qa,
    run_demo_render,
    run_demo_storyboard,
    run_demo_validate,
)


def _parse_args() -> argparse.Namespace:
    """解析命令行。"""
    parser = argparse.ArgumentParser(description="视频生产线 E2E 演示")
    parser.add_argument("--project", default=DEFAULT_DEMO_PROJECT_ID, help="project_id")
    parser.add_argument(
        "--demo-mode",
        choices=[DEMO_MODE_STEP, DEMO_MODE_PIPELINE],
        default=DEMO_MODE_STEP,
        help="step=逐步 API；pipeline=G2+管线",
    )
    parser.add_argument(
        "--pipeline-mode",
        choices=[PIPELINE_MODE_SYNC, PIPELINE_MODE_ASYNC],
        default=PIPELINE_MODE_SYNC,
        help="pipeline 模式下 sync 或 async",
    )
    parser.add_argument(
        "--av-mode",
        choices=[AV_MODE_STUB, AV_MODE_REAL],
        default=AV_MODE_STUB,
        help="real 时断言 timeline.mp4 落盘",
    )
    return parser.parse_args()


def main() -> None:
    """按序执行演示步骤并打印 JSON 摘要。"""
    if not is_postgres_configured():
        raise SystemExit("未配置 DATABASE_URL")
    args = _parse_args()
    summary = _run_demo(args.project, args.demo_mode, args.pipeline_mode, args.av_mode)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def _run_demo(project_id: str, demo_mode: str, pipeline_mode: str, av_mode: str) -> dict:
    """在单 Session 作用域内执行演示。"""
    with postgres_session_scope() as session:
        if demo_mode == DEMO_MODE_PIPELINE:
            summary = _execute_pipeline_demo(session, project_id, pipeline_mode)
        else:
            summary = _execute_step_demo(session, project_id)
    if av_mode == AV_MODE_REAL:
        compose_part = summary.get("compose") or summary.get("pipeline", {}).get("compose_output") or {}
        summary["av_assert"] = assert_real_av_compose(compose_part if isinstance(compose_part, dict) else {})
    return summary


def _execute_step_demo(session, project_id: str) -> dict:
    """逐步 API 演示（阶段 C）。"""
    ensure_demo_project(session, project_id)
    storyboard = run_demo_storyboard(session, project_id, FIXTURE_STORYBOARD)
    run_demo_bible(session, project_id, FIXTURE_BIBLE)
    validated = run_demo_validate(session, project_id)
    rendered = run_demo_render(session, project_id)
    qa = run_demo_qa(session, project_id)
    audio = run_demo_audio(session, project_id)
    compose = _safe_compose(session, project_id)
    return {
        "demo_mode": DEMO_MODE_STEP,
        "project_id": project_id,
        "storyboard": storyboard,
        "validate": validated,
        "render": rendered,
        "qa": qa,
        "audio": audio,
        "compose": compose,
        "g3_assert": assert_subtitles_burned_field(compose),
    }


def _execute_pipeline_demo(session, project_id: str, pipeline_mode: str) -> dict:
    """G2 + 管线 + G3 断言演示（阶段 E4）。"""
    ensure_demo_project(session, project_id)
    g2 = run_demo_plan_storyboard(session, project_id)
    run_demo_bible(session, project_id, FIXTURE_BIBLE)
    validated = run_demo_validate(session, project_id)
    pipeline = run_demo_pipeline(session, project_id, pipeline_mode)
    g3_source = pipeline.get("compose_output") or pipeline
    return {
        "demo_mode": DEMO_MODE_PIPELINE,
        "pipeline_mode": pipeline_mode,
        "project_id": project_id,
        "g2_storyboard": g2,
        "validate": validated,
        "pipeline": pipeline,
        "g3_assert": assert_subtitles_burned_field(g3_source),
    }


def _safe_compose(session, project_id: str) -> dict:
    """合成；阻断时返回错误摘要而非崩溃。"""
    try:
        return run_demo_compose(session, project_id)
    except ComposeBlockedError as exc:
        return {"error": "compose_blocked", "reasons": exc.reasons}


if __name__ == "__main__":
    main()
