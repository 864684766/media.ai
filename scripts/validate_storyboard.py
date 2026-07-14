"""校验 project 分镜实体引用 CLI（V2）。

【运行】
    poetry run python scripts/validate_storyboard.py --project demo
"""

import argparse
import json

from app.services.entity_validation_service import validate_project_entities
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def main() -> None:
    """执行 validate 并打印 JSON 结果。"""
    parser = argparse.ArgumentParser(description="校验分镜 bible 引用")
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    if not is_postgres_configured():
        print("未配置 DATABASE_URL")
        return
    with postgres_session_scope() as session:
        result = validate_project_entities(session, args.project)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
