"""策划→分镜业务异常。"""


class CreativePlanStoryboardError(Exception):
    """策划→分镜基础异常。"""


class CreativePlanStoryboardNotFoundError(CreativePlanStoryboardError):
    """大纲不存在。"""

    def __init__(self, plan_id: str) -> None:
        """记录 plan_id。"""
        super().__init__(plan_id)
        self.plan_id = plan_id


class CreativePlanStoryboardStatusError(CreativePlanStoryboardError):
    """大纲状态不允许生成分镜。"""


class CreativePlanStoryboardTypeError(CreativePlanStoryboardError):
    """创作类型不支持分镜生成。"""


class CreativePlanStoryboardProjectError(CreativePlanStoryboardError):
    """缺少 project_id。"""


class CreativePlanStoryboardParseError(CreativePlanStoryboardError):
    """LLM 输出无法解析为分镜数组。"""
