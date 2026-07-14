"""流水线步骤目录（V6 前端进度用）。"""

from app.core.video_constants import (
    PIPELINE_STEP_COMPOSE,
    PIPELINE_STEP_QA,
    PIPELINE_STEP_RENDER,
    PIPELINE_STEP_STORYBOARD,
    PIPELINE_STEP_VALIDATE,
    SHOT_STATUS_COMPOSED,
    SHOT_STATUS_DRAFT,
    SHOT_STATUS_QA_PASSED,
    SHOT_STATUS_RENDERED,
    SHOT_STATUS_VALIDATED,
)


def build_pipeline_steps(status_counts: dict[str, int]) -> list[dict]:
    """根据状态计数生成步骤进度。

    参数:
        status_counts: status → 镜头数。

    返回:
        list[dict]: 步骤 id、label、done、total。
    """
    total = sum(status_counts.values())
    return [
        _step(PIPELINE_STEP_STORYBOARD, "分镜入库", total, total),
        _step(PIPELINE_STEP_VALIDATE, "实体校验", _count_at_least(status_counts, SHOT_STATUS_VALIDATED), total),
        _step(PIPELINE_STEP_RENDER, "渲染切片", _count_at_least(status_counts, SHOT_STATUS_RENDERED), total),
        _step(PIPELINE_STEP_QA, "连续性 QA", _count_at_least(status_counts, SHOT_STATUS_QA_PASSED), total),
        _step(PIPELINE_STEP_COMPOSE, "时间轴合成", status_counts.get(SHOT_STATUS_COMPOSED, 0), total),
    ]


def _count_at_least(counts: dict[str, int], threshold_status: str) -> int:
    """统计达到某阶段及之后的镜头数。"""
    order = [
        SHOT_STATUS_DRAFT,
        SHOT_STATUS_VALIDATED,
        SHOT_STATUS_RENDERED,
        SHOT_STATUS_QA_PASSED,
        SHOT_STATUS_COMPOSED,
    ]
    try:
        idx = order.index(threshold_status)
    except ValueError:
        return 0
    allowed = set(order[idx:])
    return sum(v for k, v in counts.items() if k in allowed)


def _step(step_id: str, label: str, done: int, total: int) -> dict:
    """构造单步进度对象。"""
    return {"id": step_id, "label": label, "done_count": done, "total_count": total}
