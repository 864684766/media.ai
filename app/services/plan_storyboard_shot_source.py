"""策划→分镜镜头数据来源（LLM 或模板）。"""

import json

from app.creative.plan_storyboard_prompt_builder import build_plan_storyboard_user_prompt
from app.creative.plan_storyboard_template_shot_builder import build_template_shots_from_content
from app.core.plan_storyboard_constants import PLAN_STORYBOARD_SKILL_ID
from app.models.postgres.creative_plan_model import CreativePlanModel
from app.schemas.video_shot import ShotInput
from app.services.plan_storyboard_llm_runner import run_plan_storyboard_llm
from app.services.plan_storyboard_shot_normalizer import normalize_storyboard_shots
from app.skills import load_skill_context
from app.video.storyboard_json_parser import parse_storyboard_json_array


def resolve_shots_for_plan(row: CreativePlanModel) -> list[ShotInput]:
    """优先 LLM 拆镜，失败或无 Key 时用模板 fallback。

    参数:
        row: 已确认视频大纲 ORM。

    返回:
        list[ShotInput]: 规范化后的镜头列表。
    """
    llm_shots = _try_llm_shots(row)
    if llm_shots:
        return llm_shots
    content = json.loads(row.content_json or "{}")
    return build_template_shots_from_content(content)


def _try_llm_shots(row: CreativePlanModel) -> list[ShotInput] | None:
    """尝试 LLM 解析分镜；失败返回 None。"""
    prompt = build_plan_storyboard_user_prompt(row.content_md)
    skill = load_skill_context(skill_id=PLAN_STORYBOARD_SKILL_ID, creation_type=row.creation_type)
    text = run_plan_storyboard_llm(prompt, skill.system_prompt)
    if not text.strip():
        return None
    try:
        rows = parse_storyboard_json_array(text)
    except ValueError:
        return None
    return normalize_storyboard_shots(rows)
