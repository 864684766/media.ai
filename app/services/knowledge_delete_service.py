"""知识库文档删除服务。"""

from sqlalchemy.orm import Session

from app.storage.postgres.document_repository import DocumentRepository


class KnowledgeDocumentNotFoundError(Exception):
    """文档不存在。"""

    def __init__(self, document_id: str) -> None:
        """记录 document_id。"""
        super().__init__(document_id)
        self.document_id = document_id


def delete_knowledge_document(session: Session, document_id: str) -> None:
    """删除文档及其 chunks。

    参数:
        session: DB Session。
        document_id: 文档 id。

    异常:
        KnowledgeDocumentNotFoundError: 文档不存在。
    """
    deleted = DocumentRepository(session).delete_document(document_id)
    if not deleted:
        raise KnowledgeDocumentNotFoundError(document_id)
