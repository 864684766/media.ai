"""视频子图 review_gate 节点（HITL 暂停）。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import (
    PAUSE_REASON_AWAITING_REVIEW,
    PIPELINE_RUN_PAUSED,
)
from app.graph.video_pipeline_constants import NODE_REVIEW_GATE
from app.graph.video_pipeline_shot_counter import count_awaiting_review
from app.schemas.video_pipeline_state import VideoPipelineState


def run_review_gate_step(session: Session, state: VideoPipelineState) -> dict:
    """检测 awaiting_review 并决定是否暂停。

    参数:
        session: PG Session。
        state: 子图状态。

    返回:
        dict: 写入 state 的字段更新。
    """
    awaiting = count_awaiting_review(session, state.project_id)
    base = {
        "current_step": NODE_REVIEW_GATE,
        "steps_completed": [*state.steps_completed, NODE_REVIEW_GATE],
    }
    if awaiting > 0:
        base.update(
            {
                "paused": True,
                "pause_reason": PAUSE_REASON_AWAITING_REVIEW,
                "run_status": PIPELINE_RUN_PAUSED,
                "qa_awaiting_count": awaiting,
            },
        )
    return base
