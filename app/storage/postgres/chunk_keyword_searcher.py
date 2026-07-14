"""PostgreSQL 关键词检索器（Hybrid 检索的关键词路）。

【职责】
    在 chunks 表上做关键词召回，返回带分数的 chunk 列表。
    对应 docs/ARCHITECTURE.html sec-06.2 的「关键词路」。

【为什么用 LIKE 而不是 tsvector】
    PG 的 tsvector 依赖分词器，对中文需要额外安装 zhparser 等扩展；
    第一版为保证「本地 SQLite 测试 / 远程 PG」行为一致，采用
    「切词（含中文 bigram）+ LIKE 命中计数」的朴素打分。
    生产可平滑升级：只需替换本文件实现，接口不变。

【切词与打分】
    见 app/storage/postgres/keyword_scoring_helper.py。
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.postgres.chunk_model import ChunkModel
from app.storage.postgres.keyword_scoring_helper import score_text, split_terms

# LIKE 模式模板：%词%
LIKE_PATTERN_TEMPLATE = "%{term}%"


class ChunkKeywordSearcher:
    """chunks 表关键词召回。

    参数说明:
        session: SQLAlchemy Session。
    """

    def __init__(self, session: Session) -> None:
        """绑定数据库 Session。"""
        self._session = session

    def search(
        self,
        query: str,
        project_id: str | None,
        top_k: int,
    ) -> list[tuple[ChunkModel, float]]:
        """按关键词召回 chunks。

        参数:
            query: 查询文本。
            project_id: 项目过滤；None 时不过滤。
            top_k: 最多返回条数。

        返回:
            list[tuple[ChunkModel, float]]: (chunk, 得分) 按得分降序。
        """
        terms = split_terms(query)
        if not terms:
            return []
        candidates = self._query_candidates(terms, project_id)
        scored = [(chunk, score_text(chunk.text, terms)) for chunk in candidates]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def _query_candidates(
        self,
        terms: list[str],
        project_id: str | None,
    ) -> list[ChunkModel]:
        """查询命中任意词的候选 chunks。"""
        query = self._session.query(ChunkModel)
        if project_id is not None:
            query = query.filter(ChunkModel.project_id == project_id)
        patterns = [LIKE_PATTERN_TEMPLATE.format(term=term) for term in terms]
        conditions = [ChunkModel.text.like(pattern) for pattern in patterns]
        return query.filter(or_(*conditions)).all()
