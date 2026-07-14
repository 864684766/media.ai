"""创作大纲业务异常。"""


class ClarificationRequiredError(Exception):
    """requires_clarification 为真但无可用澄清摘要。"""


class CreativePlanNotFoundError(Exception):
    """大纲不存在。"""


class CreativePlanStatusError(Exception):
    """大纲状态不允许当前操作。"""


class CreativePlanRevisionLimitError(Exception):
    """改稿次数超限。"""
