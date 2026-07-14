"""提交结构化分镜 CLI（V1）。

【用途】
    从 JSON 文件解析 Shot 数组并写入 PostgreSQL shots 表。

【运行】
    poetry run python scripts/submit_storyboard.py --project demo --file shots.json

【边界】
    需配置 DATABASE_URL；行为受 config/app.yaml video.storyboard 控制。
"""

import argparse
import json
from pathlib import Path

from app.schemas.video_shot import ShotInput, StoryboardSubmitRequest
from app.services.storyboard_service import submit_storyboard
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured
from app.video.storyboard_json_parser import parse_storyboard_json_array


def _load_shots(path: Path) -> list[ShotInput]:
    """从文件读取并校验分镜数组。

    参数:
        path: JSON 文件路径。

    返回:
        list[ShotInput]: 校验后的镜头列表。
    """
    raw = path.read_text(encoding="utf-8")
    rows = parse_storyboard_json_array(raw)
    return [ShotInput.model_validate(row) for row in rows]


def _print_result(payload: dict) -> None:
    """打印入库结果摘要。

    参数:
        payload: StoryboardSubmitResponse 序列化字典。
    """
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    """解析参数、提交分镜、打印响应 JSON。"""
    parser = argparse.ArgumentParser(description="提交结构化分镜到 shots 表")
    parser.add_argument("--project", required=True, help="项目 id，如 demo")
    parser.add_argument("--file", required=True, help="分镜 JSON 文件路径")
    args = parser.parse_args()
    if not is_postgres_configured():
        print("未配置 DATABASE_URL，无法提交分镜。")
        return
    shots = _load_shots(Path(args.file))
    request = StoryboardSubmitRequest(shots=shots)
    with postgres_session_scope() as session:
        response = submit_storyboard(session, args.project, request)
    _print_result(response.model_dump())


if __name__ == "__main__":
    main()
