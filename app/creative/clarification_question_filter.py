"""根据 brief 信号过滤澄清题、生成预填答案。"""

from app.creative.clarification_brief_extractor import BriefSignals, signal_for_question
from app.schemas.clarification import ClarificationAnswerItem, ClarificationQuestionItem


def filter_questions_by_brief(
    questions: list[ClarificationQuestionItem],
    signals: BriefSignals,
) -> list[ClarificationQuestionItem]:
    """去掉 brief 中已明确给出的维度，避免重复追问。"""
    return [q for q in questions if signal_for_question(signals, q.question_id) is None]


def build_prefilled_answers(
    all_questions: list[ClarificationQuestionItem],
    signals: BriefSignals,
) -> list[ClarificationAnswerItem]:
    """将 brief 已识别维度转为结构化答案。"""
    answers: list[ClarificationAnswerItem] = []
    for q in all_questions:
        option_id = signal_for_question(signals, q.question_id)
        if option_id:
            answers.append(ClarificationAnswerItem(question_id=q.question_id, option_id=option_id))
    return answers


def merge_answer_lists(
    prefilled: list[ClarificationAnswerItem],
    submitted: list[ClarificationAnswerItem],
) -> list[ClarificationAnswerItem]:
    """合并预填与用户提交，用户提交优先。"""
    by_qid = {item.question_id: item for item in prefilled}
    for item in submitted:
        by_qid[item.question_id] = item
    return list(by_qid.values())
