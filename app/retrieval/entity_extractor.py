"""实体抽取（GraphRAG 入口）。

【职责】
    从用户问题抽取可用于图谱扩展的实体名（规则 + 可选 LLM）。
"""

import re

ENTITY_PATTERN = re.compile(r"[\u4e00-\u9fff]{2,4}")


def extract_entities(question: str, max_count: int = 3) -> list[str]:
    """抽取问题中的中文实体候选。

    参数:
        question: 用户问题。
        max_count: 最多返回几个。

    返回:
        list[str]: 实体名列表（去重）。
    """
    matches = ENTITY_PATTERN.findall(question)
    unique: list[str] = []
    for name in matches:
        if name not in unique:
            unique.append(name)
        if len(unique) >= max_count:
            break
    return unique
