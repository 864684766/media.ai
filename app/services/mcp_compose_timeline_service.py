"""MCP compose_timeline 合成服务。"""

from sqlalchemy.orm import Session

from app.services.compose_job_service import ComposeBlockedError, start_compose_job


def compose_timeline_for_mcp(session: Session, project_id: str) -> dict:
    """将 qa_passed 镜头合成时间轴成片。

    参数:
        session: PG Session。
        project_id: 项目 id。

    返回:
        dict: output_uri 与 job_id。
    """
    try:
        result = start_compose_job(session, project_id)
    except ComposeBlockedError as exc:
        raise ValueError(exc.reasons[0] if exc.reasons else "compose blocked") from exc
    return {
        "project_id": project_id,
        "job_id": result.job.job_id,
        "output_uri": result.output.uri,
        "subtitles_burned": result.output.subtitles_burned,
    }
