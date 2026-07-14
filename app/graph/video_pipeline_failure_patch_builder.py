"""视频子图：步骤失败 patch 构造。"""

from app.core.video_pipeline_run_constants import PIPELINE_RUN_FAILED


def build_pipeline_failure_patch(base: dict, message: str) -> dict:
    """将节点失败写入 state（供 Job checkpoint 与 UI 展示）。

    参数:
        base: 节点已构造的部分更新。
        message: 用户可读错误说明。

    返回:
        dict: 含 run_status=failed 与 error_message。
    """
    base["run_status"] = PIPELINE_RUN_FAILED
    base["error_message"] = message
    return base
