"""从视频大纲 content_json 生成模板分镜（无 API Key 时 fallback）。"""

from app.core.plan_storyboard_constants import DEFAULT_TEMPLATE_SHOT_SIZE
from app.schemas.video_shot import ShotInput


def build_template_shots_from_content(content_json: dict) -> list[ShotInput]:
    """按 segments 字段拆成 ShotInput 列表。

    参数:
        content_json: creative_plans.content_json 反序列化结果。

    返回:
        list[ShotInput]: 至少一条镜头；无 segments 时生成单镜占位。
    """
    segments = content_json.get("segments") or []
    if not segments:
        return [_fallback_shot(content_json)]
    return [_segment_to_shot(index, segment) for index, segment in enumerate(segments)]


def _segment_to_shot(index: int, segment: dict) -> ShotInput:
    """单段策划 → 单镜。"""
    start_sec = int(segment.get("start_sec", 0))
    end_sec = int(segment.get("end_sec", start_sec + 3))
    duration = max(float(end_sec - start_sec), 1.0)
    visual = str(segment.get("visual", "")).strip() or "待补画面"
    mood = str(segment.get("mood", "")).strip()
    action = f"{visual}（{mood}）" if mood else visual
    return ShotInput(
        shot_no=str(index + 1),
        duration_sec=duration,
        shot_size=DEFAULT_TEMPLATE_SHOT_SIZE,
        action=action,
    )


def _fallback_shot(content_json: dict) -> ShotInput:
    """无 segments 时的单镜占位。"""
    hook = str(content_json.get("hook", "")).strip() or "开场画面"
    return ShotInput(shot_no="1", duration_sec=3.0, shot_size=DEFAULT_TEMPLATE_SHOT_SIZE, action=hook)
