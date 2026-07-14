"""知识库文档列表查询。"""

from sqlalchemy.orm import Session

from app.models.postgres.document_model import DocumentModel


def query_documents(session: Session, project_id: str | None, limit: int) -> list[DocumentModel]:
    """按项目过滤查询文档列表。

    参数:
        session: SQLAlchemy Session。
        project_id: 可选项目 id。
        limit: 最多条数。

    返回:
        list[DocumentModel]: 文档 ORM 列表。
    """
    query = session.query(DocumentModel)
    if project_id:
        query = query.filter(DocumentModel.project_id == project_id)
    return query.order_by(DocumentModel.created_at.desc()).limit(limit).all()
