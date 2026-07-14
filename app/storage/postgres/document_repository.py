"""PostgreSQL 文档与 chunk Repository。

【职责】
    封装 documents / chunks 表的写入与读取，供 Ingestion 写库
    （app/ingestion/database_feed_adapter.py）与检索链使用。

【幂等设计】
    同一 document_id 重复导入时采用「先删旧 chunks 再写新」的覆盖策略，
    保证重跑 Ingestion 不产生重复数据（对应"Neo4j 可重建"的同一思想）。
"""

from sqlalchemy.orm import Session

from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument
from app.models.postgres.chunk_model import ChunkModel
from app.models.postgres.document_model import DocumentModel


class DocumentRepository:
    """文档与 chunk 持久化。

    参数说明:
        session: 由 postgres_session_scope 提供的 SQLAlchemy Session。
    """

    def __init__(self, session: Session) -> None:
        """绑定数据库 Session。

        参数:
            session: 当前任务使用的 Session。
        """
        self._session = session

    def upsert_document(self, document: IngestionDocument) -> DocumentModel:
        """写入或覆盖一篇文档（真相源）。

        参数:
            document: Ingestion 文档模型。

        返回:
            DocumentModel: 已保存的 ORM 对象。
        """
        model = self._session.get(DocumentModel, document.document_id)
        if model is None:
            model = DocumentModel(id=document.document_id)
            self._session.add(model)
        model.project_id = document.project_id
        model.source = document.source
        model.text = document.text
        self._session.commit()
        return model

    def replace_chunks(self, document_id: str, chunks: list[IngestionChunk]) -> int:
        """覆盖式写入文档的全部 chunks（先删旧、再写新，保证幂等）。

        参数:
            document_id: 文档 id。
            chunks: 切分后的 chunk 列表。

        返回:
            int: 本次写入的 chunk 数量。
        """
        self._delete_chunks(document_id)
        for chunk in chunks:
            self._session.add(_to_chunk_model(chunk))
        self._session.commit()
        return len(chunks)

    def list_chunks(self, document_id: str) -> list[ChunkModel]:
        """按序读取文档的全部 chunks。

        参数:
            document_id: 文档 id。

        返回:
            list[ChunkModel]: 按 chunk_index 升序的 chunk 列表。
        """
        query = self._session.query(ChunkModel)
        query = query.filter(ChunkModel.document_id == document_id)
        return query.order_by(ChunkModel.chunk_index.asc()).all()

    def get_document(self, document_id: str) -> DocumentModel | None:
        """按 id 读取文档。

        参数:
            document_id: 文档 id。

        返回:
            DocumentModel | None: 存在则 ORM，否则 None。
        """
        return self._session.get(DocumentModel, document_id)

    def delete_document(self, document_id: str) -> bool:
        """删除文档及其全部 chunks。

        参数:
            document_id: 文档 id。

        返回:
            bool: 删除成功 True；不存在 False。
        """
        model = self.get_document(document_id)
        if model is None:
            return False
        self._delete_chunks(document_id)
        self._session.delete(model)
        self._session.commit()
        return True

    def _delete_chunks(self, document_id: str) -> None:
        """删除文档现有 chunks（replace_chunks 的第一步）。"""
        query = self._session.query(ChunkModel)
        query.filter(ChunkModel.document_id == document_id).delete()


def _to_chunk_model(chunk: IngestionChunk) -> ChunkModel:
    """把 IngestionChunk 转换为 ORM 模型。

    参数:
        chunk: Ingestion 切分结果。

    返回:
        ChunkModel: 可直接 add 的 ORM 对象。
    """
    return ChunkModel(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        project_id=chunk.project_id,
        chunk_index=chunk.index,
        text=chunk.text,
        source=chunk.source,
    )
