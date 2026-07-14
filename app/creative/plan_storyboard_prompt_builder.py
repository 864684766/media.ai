"""策划→分镜用户 prompt 构造。"""

from app.core.plan_storyboard_constants import PLAN_STORYBOARD_PROMPT_INTRO


def build_plan_storyboard_user_prompt(content_md: str) -> str:
    """将已确认大纲 Markdown 拼成 LLM 用户输入。

    参数:
        content_md: creative_plans.content_md。

    返回:
        str: 供 Provider 使用的用户消息。
    """
    body = content_md.strip() or "（大纲正文为空，请按通用短视频结构拆镜）"
    return f"{PLAN_STORYBOARD_PROMPT_INTRO}\n\n{body}"
