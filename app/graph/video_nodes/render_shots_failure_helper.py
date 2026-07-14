"""render_shots 节点失败处理。"""

from app.core.video_pipeline_run_constants import PIPELINE_RUN_FAILED
from app.graph.video_pipeline_failure_patch_builder import build_pipeline_failure_patch
from app.video.project_budget_gate import BudgetExceededError


def patch_render_budget_failure(base: dict, exc: BudgetExceededError) -> dict:
    """预算熔断失败 patch。"""
    message = f"budget exceeded: {exc.total_cost_usd:.4f}/{exc.budget_limit_usd:.4f}"
    return build_pipeline_failure_patch(base, message)


def patch_render_generic_failure(base: dict, exc: Exception) -> dict:
    """通用渲染失败 patch。"""
    return build_pipeline_failure_patch(base, str(exc))
