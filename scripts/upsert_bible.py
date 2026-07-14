"""upsert 视频 bible CLI（V2）。

【运行】
    poetry run python scripts/upsert_bible.py --project demo --kind all --file scripts/fixtures/demo-bible.json
"""

import argparse
import json
from pathlib import Path

from app.schemas.video_bible import (
    CharacterBibleInput,
    CharacterBibleUpsertRequest,
    PropInventoryInput,
    PropInventoryUpsertRequest,
    SceneLockInput,
    SceneLockUpsertRequest,
)
from app.services.bible_service import upsert_characters, upsert_props, upsert_scenes
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

_KIND_CHARACTERS = "characters"
_KIND_SCENES = "scenes"
_KIND_PROPS = "props"
_KIND_ALL = "all"


def _load_json(path: Path) -> dict:
    """读取 JSON 文件为字典。"""
    return json.loads(path.read_text(encoding="utf-8"))


def _upsert_kind(session, project_id: str, kind: str, data: dict) -> None:
    """按 kind 调用对应 upsert 服务。"""
    if kind in (_KIND_CHARACTERS, _KIND_ALL) and data.get("characters"):
        req = CharacterBibleUpsertRequest(
            characters=[CharacterBibleInput.model_validate(x) for x in data["characters"]],
        )
        upsert_characters(session, project_id, req)
    if kind in (_KIND_SCENES, _KIND_ALL) and data.get("scenes"):
        req = SceneLockUpsertRequest(
            scenes=[SceneLockInput.model_validate(x) for x in data["scenes"]],
        )
        upsert_scenes(session, project_id, req)
    if kind in (_KIND_PROPS, _KIND_ALL) and data.get("props"):
        req = PropInventoryUpsertRequest(
            props=[PropInventoryInput.model_validate(x) for x in data["props"]],
        )
        upsert_props(session, project_id, req)


def main() -> None:
    """解析参数并 upsert bible。"""
    parser = argparse.ArgumentParser(description="upsert 视频 bible")
    parser.add_argument("--project", required=True)
    parser.add_argument("--kind", choices=[_KIND_CHARACTERS, _KIND_SCENES, _KIND_PROPS, _KIND_ALL], required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    if not is_postgres_configured():
        print("未配置 DATABASE_URL")
        return
    data = _load_json(Path(args.file))
    with postgres_session_scope() as session:
        _upsert_kind(session, args.project, args.kind, data)
    print(f"bible upsert 完成: project={args.project} kind={args.kind}")


if __name__ == "__main__":
    main()
