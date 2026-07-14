"""时间轴合成 CLI（V5）。"""

import argparse

from app.services.compose_job_service import ComposeBlockedError, start_compose_job
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="合成 qa_passed 镜头时间轴 Stub")
    parser.add_argument("--project", required=True, help="project_id")
    return parser.parse_args()


def main() -> None:
    """入口：POST compose 同等逻辑。"""
    if not is_postgres_configured():
        raise SystemExit("未配置 DATABASE_URL")
    args = _parse_args()
    try:
        with postgres_session_scope() as session:
            result = start_compose_job(session, args.project)
    except ComposeBlockedError as exc:
        raise SystemExit(f"合成阻断: {exc.reasons}") from exc
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
