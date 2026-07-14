"""分镜入库与查询业务服务。

【职责】
    编排 Repository + video 配置：提交时是否全量替换、默认 status。

【何时调用】
    app/api/video.py 路由层调用，不直接操作 Session。
"""

from sqlalchemy.orm import Session

from app.schemas.video_shot import (
    ShotOutput,
    StoryboardListResponse,
    StoryboardSubmitRequest,
    StoryboardSubmitResponse,
)
from app.storage.postgres.shot_repository import ShotRepository
from app.video.shot_row_mapper import shot_model_to_output
from app.video.video_config_reader import load_video_storyboard_config


def submit_storyboard(
    session: Session,
    project_id: str,
    request: StoryboardSubmitRequest,
) -> StoryboardSubmitResponse:
    """提交结构化分镜并入库。

    参数:
        session: PG Session。
        project_id: 路径中的项目 id。
        request: 含 shots 数组的请求体。

    返回:
        StoryboardSubmitResponse: 替换计数与入库结果。
    """
    config = load_video_storyboard_config()
    repository = ShotRepository(session)
    replaced = 0
    if config.replace_on_submit:
        replaced = repository.delete_by_project(project_id)
    models = repository.insert_shots(
        project_id,
        request.shots,
        config.default_status,
    )
    outputs = [shot_model_to_output(model) for model in models]
    return StoryboardSubmitResponse(
        project_id=project_id,
        replaced_count=replaced,
        shots=outputs,
    )


def list_project_shots(session: Session, project_id: str) -> StoryboardListResponse:
    """列出 project 下全部分镜。

    参数:
        session: PG Session。
        project_id: 项目 id。

    返回:
        StoryboardListResponse: 按镜号排序的列表。
    """
    repository = ShotRepository(session)
    models = repository.list_by_project(project_id)
    outputs: list[ShotOutput] = [shot_model_to_output(model) for model in models]
    return StoryboardListResponse(project_id=project_id, shots=outputs)
