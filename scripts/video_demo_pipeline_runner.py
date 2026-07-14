"""视频 E2E 演示 D1/D3 管线路径。"""

from sqlalchemy.orm import Session

from app.services.video_pipeline_async_service import execute_pipeline_job, start_async_pipeline_job
from app.services.video_pipeline_run_service import run_video_pipeline
from video_demo_constants import PIPELINE_MODE_ASYNC, PIPELINE_MODE_SYNC


def run_demo_pipeline(session: Session, project_id: str, mode: str) -> dict:
    """按 sync 或 async 执行 LangGraph 管线。

    参数:
        session: PG Session。
        project_id: 项目 id。
        mode: sync 或 async。

    返回:
        dict: 运行结果 model_dump。
    """
    if mode == PIPELINE_MODE_ASYNC:
        return _run_async_pipeline(session, project_id)
    return run_video_pipeline(session, project_id).model_dump()


def _run_async_pipeline(session: Session, project_id: str) -> dict:
    """创建 Job 并同步执行（脚本内不启线程）。"""
    job_id = start_async_pipeline_job(session, project_id)
    result = execute_pipeline_job(session, job_id)
    payload = result.model_dump()
    payload["job_id"] = job_id
    return payload
