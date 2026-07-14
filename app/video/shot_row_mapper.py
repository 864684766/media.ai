"""Shot ORM 与 Pydantic 互转辅助。

【职责】
    将 ShotInput / ShotModel 映射，避免 Repository 内联字段赋值。
"""

from app.models.postgres.shot_model import ShotModel
from app.schemas.video_shot import ShotInput, ShotOutput
from app.video.shot_id_helper import new_shot_id


def shot_input_to_model(
    project_id: str,
    payload: ShotInput,
    status: str,
) -> ShotModel:
    """把提交条目转为 ORM 行（生成新 shot_id）。

    参数:
        project_id: 项目 id。
        payload: API 入参单条镜头。
        status: 初始状态。

    返回:
        ShotModel: 待 persist 的 ORM 实例（未 commit）。
    """
    return ShotModel(
        shot_id=new_shot_id(),
        project_id=project_id,
        shot_no=payload.shot_no,
        duration_sec=payload.duration_sec,
        shot_size=payload.shot_size,
        camera=payload.camera,
        action=payload.action,
        dialogue=payload.dialogue,
        sfx=payload.sfx,
        character_ids=list(payload.character_ids),
        scene_id=payload.scene_id,
        prop_ids=list(payload.prop_ids),
        transition=payload.transition,
        status=status,
    )


def shot_model_to_output(model: ShotModel) -> ShotOutput:
    """ORM 行转 API 响应条目。

    参数:
        model: 已持久化的 ShotModel。

    返回:
        ShotOutput: 对外契约对象。
    """
    return ShotOutput(
        shot_id=model.shot_id,
        project_id=model.project_id,
        shot_no=model.shot_no,
        duration_sec=model.duration_sec,
        shot_size=model.shot_size,
        camera=model.camera,
        action=model.action,
        dialogue=model.dialogue,
        sfx=model.sfx,
        character_ids=list(model.character_ids or []),
        scene_id=model.scene_id,
        prop_ids=list(model.prop_ids or []),
        keyframe_uri=model.keyframe_uri or "",
        transition=model.transition,
        status=model.status,
        qa_attempts=model.qa_attempts,
    )
