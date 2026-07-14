"""关键词切词与打分辅助。

【职责】
    为 ChunkKeywordSearcher 提供查询切词与命中打分。

【中文如何切词】
    中文没有空格分词，整句 LIKE 几乎无法命中。
    做法：先按空白切出 token；对含中文且长度 > 2 的 token，
    再补充「二字组（bigram）」作为检索词。
    例：「张三的师父」 -> ["张三的师父", "张三", "三的", "的师", "师父"]

【打分规则】
    每命中一个词得 1 分；bigram 让语义相近的片段也能得到部分分数。
"""

import re

# 中文字符匹配（CJK 统一表意文字区）
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")

# 触发 bigram 拆分的最小 token 长度
BIGRAM_MIN_TOKEN_LENGTH = 3

# 单个 bigram 的长度
BIGRAM_SIZE = 2


def split_terms(query: str) -> list[str]:
    """把查询切成检索词列表（空白 token + 中文 bigram）。

    参数:
        query: 查询文本。

    返回:
        list[str]: 去重后的检索词列表；全空白时为空列表。
    """
    tokens = [token for token in query.split() if token]
    terms: list[str] = []
    for token in tokens:
        terms.append(token)
        terms.extend(_cjk_bigrams(token))
    # dict.fromkeys 去重且保持顺序
    return list(dict.fromkeys(terms))


def score_text(text: str, terms: list[str]) -> float:
    """按命中词数给文本打分。

    参数:
        text: chunk 文本。
        terms: 检索词列表。

    返回:
        float: 命中词数（每命中一个词 +1）。
    """
    return float(sum(1 for term in terms if term in text))


def _cjk_bigrams(token: str) -> list[str]:
    """对含中文的长 token 生成二字组列表。

    参数:
        token: 单个查询词。

    返回:
        list[str]: bigram 列表；非中文或过短时为空列表。
    """
    if len(token) < BIGRAM_MIN_TOKEN_LENGTH or not CJK_PATTERN.search(token):
        return []
    return [token[i : i + BIGRAM_SIZE] for i in range(len(token) - 1)]
