"""澄清答案合并与需求摘要生成。"""

import json

from app.core.clarification_brief_constants import BRIEF_SECTION_USER
from app.schemas.clarification import ClarificationAnswerItem, ClarificationQuestionItem


def merge_answers_json(existing_json: str, new_answers: list[ClarificationAnswerItem]) -> str:
    """将新答案合并进 answers_json。"""
    current = _load_answers(existing_json)
    current.extend([item.model_dump() for item in new_answers])
    return json.dumps(current, ensure_ascii=False)


def build_requirements_summary(
    creation_type: str,
    questions: list[ClarificationQuestionItem],
    answers: list[dict],
    initial_brief: str = "",
) -> str:
    """根据题目、答案与用户 brief 生成 Markdown 摘要。"""
    label_map = _option_label_map(questions)
    lines = [f"## 创作需求摘要（{creation_type}）", ""]
    if initial_brief.strip():
        lines.append(f"**{BRIEF_SECTION_USER}**：{initial_brief.strip()}")
        lines.append("")
    for item in answers:
        line = _format_answer_line(item, label_map)
        if line:
            lines.append(line)
    return "\n".join(lines)


def format_clarification_user_message(answers: list[ClarificationAnswerItem]) -> str:
    """将结构化回答转为可持久化的用户消息文本。"""
    parts = [f"{a.question_id}={a.option_id or a.custom_text}" for a in answers]
    return "【澄清偏好】" + "；".join(parts)


def _format_answer_line(item: dict, label_map: dict[str, dict[str, str]]) -> str:
    """格式化单行摘要。"""
    qid = str(item.get("question_id", ""))
    option_id = item.get("option_id")
    custom = item.get("custom_text")
    if option_id:
        label = label_map.get(qid, {}).get(str(option_id), str(option_id))
        return f"- **{qid}**：{label}"
    if custom:
        return f"- **{qid}**：{custom}"
    return ""


def _option_label_map(questions: list[ClarificationQuestionItem]) -> dict[str, dict[str, str]]:
    """题目 id → option_id → label。"""
    result: dict[str, dict[str, str]] = {}
    for q in questions:
        result[q.question_id] = {opt.option_id: opt.label for opt in q.options}
    return result


def _load_answers(raw: str) -> list[dict]:
    """解析 answers_json。"""
    if not raw.strip():
        return []
    data = json.loads(raw)
    return data if isinstance(data, list) else []
