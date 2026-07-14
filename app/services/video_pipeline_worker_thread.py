"""视频管线后台 Worker 线程。"""

import threading

from app.services.video_pipeline_async_service import execute_pipeline_job
from app.storage.postgres.postgres_session_scope import postgres_session_scope


def spawn_pipeline_worker(job_id: str) -> None:
    """在后台线程执行管线 Job。

    参数:
        job_id: 已创建的 Job id。
    """
    thread = threading.Thread(target=_run_job_in_thread, args=(job_id,), daemon=True)
    thread.start()


def _run_job_in_thread(job_id: str) -> None:
    """线程入口：独立 Session 执行 Job。"""
    try:
        with postgres_session_scope() as session:
            execute_pipeline_job(session, job_id)
    except Exception:
        return
