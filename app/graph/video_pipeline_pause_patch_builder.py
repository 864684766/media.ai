"""视频子图：暂停 patch 构造。"""

from app.core.video_pipeline_run_constants import PIPELINE_RUN_PAUSED


def build_pipeline_pause_patch(
    current_step: str,
    pause_reason: str,
    steps_completed: list[str],
) -> dict:
    """构造暂停更新（不追加当前步到 steps_completed）。

    参数:
        current_step: 当前节点 id。
        pause_reason: 暂停原因码。
        steps_completed: 已有完成列表。

    返回:
        dict: 写入 VideoPipelineState 的字段。
    """
    return {
        "current_step": current_step,
        "pause_reason": pause_reason,
        "paused": True,
        "run_status": PIPELINE_RUN_PAUSED,
        "steps_completed": steps_completed,
    }
