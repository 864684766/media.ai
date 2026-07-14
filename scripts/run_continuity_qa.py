"""连续性 QA CLI（V4）。"""

import argparse

from app.services.continuity_qa_service import run_continuity_qa
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="对 rendered 镜头执行连续性 QA")
    parser.add_argument("--project", required=True, help="project_id")
    return parser.parse_args()


def main() -> None:
    """入口：POST qa 同等逻辑。"""
    if not is_postgres_configured():
        raise SystemExit("未配置 DATABASE_URL")
    args = _parse_args()
    with postgres_session_scope() as session:
        result = run_continuity_qa(session, args.project)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
