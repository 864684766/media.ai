"""Prompt 拼装辅助。

【职责】
    将 Skill、history、检索证据、用户问题拼成 state.prompt。

【拼装顺序】
    【系统人设】→【历史消息】→【作品库证据】→【联网结果】→【本轮用户】
    检索证据带 chunk_id 标注，方便模型在回答中引用来源。
    段落标题统一取自 prompt_constants.py（一处权威）。
"""

from app.graph import prompt_constants as pc
from app.schemas.agent_state import AgentState


def build_prompt_text(state: AgentState) -> str:
    """构造 prompt 文本。

    参数:
        state: 当前 AgentState。

    返回:
        str: 拼装后的 prompt。
    """
    parts = [
        _build_system_part(state),
        _build_summary_part(state),
        _build_history_part(state),
        _build_evidence_part(state),
        _build_web_part(state),
    ]
    parts.append(f"{pc.PROMPT_SECTION_QUESTION}\n{state.question}")
    return pc.PROMPT_PART_SEPARATOR.join(part for part in parts if part)


def _build_evidence_part(state: AgentState) -> str:
    """构造作品库检索证据部分（needs_project 命中时）。"""
    if state.retrieval is None or not state.retrieval.chunks:
        return ""
    lines = [f"[{chunk.chunk_id}] {chunk.text}" for chunk in state.retrieval.chunks]
    return f"{pc.PROMPT_SECTION_EVIDENCE}{pc.PROMPT_EVIDENCE_GUIDE}\n" + "\n".join(lines)


def _build_web_part(state: AgentState) -> str:
    """构造联网搜索结果部分（needs_web 或兜底命中时）。"""
    if state.retrieval is None or not state.retrieval.web_results:
        return ""
    lines = [f"- {item.title}: {item.snippet}" for item in state.retrieval.web_results]
    return f"{pc.PROMPT_SECTION_WEB}\n" + "\n".join(lines)


def _build_system_part(state: AgentState) -> str:
    """构造 system 人设部分。"""
    if state.skill is None or not state.skill.system_prompt:
        return ""
    return f"{pc.PROMPT_SECTION_SYSTEM}\n{state.skill.system_prompt}"


def _build_summary_part(state: AgentState) -> str:
    """构造历史摘要部分。"""
    if not state.history_summary:
        return ""
    return f"{pc.PROMPT_SECTION_HISTORY_SUMMARY}\n{state.history_summary}"


def _build_history_part(state: AgentState) -> str:
    """构造 history 部分。"""
    if not state.history:
        return ""
    lines = [f"{item.role}: {item.content}" for item in state.history]
    return f"{pc.PROMPT_SECTION_HISTORY}\n" + "\n".join(lines)
