"""add clarification_sessions explicit

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-13

【说明】
    增量迁移：显式创建 clarification_sessions 表（已存在则跳过）。
    适用于基线 f8a1c2b3d4e5 已 stamp 但缺澄清表的历史库。
"""

from alembic import op
import sqlalchemy as sa

from app.core.clarification_constants import CLARIFICATION_STATUS_COLLECTING
from app.storage.postgres import postgres_constants as pc

revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

_TABLE = pc.TABLE_CLARIFICATION_SESSIONS
_STATUS_DEFAULT = CLARIFICATION_STATUS_COLLECTING


def _table_exists(bind) -> bool:
    """检查 clarification_sessions 表是否已存在。"""
    inspector = sa.inspect(bind)
    return _TABLE in inspector.get_table_names()


def upgrade() -> None:
    """创建 clarification_sessions（checkfirst）。"""
    bind = op.get_bind()
    if _table_exists(bind):
        return
    op.create_table(
        _TABLE,
        sa.Column("session_id", sa.String(64), primary_key=True),
        sa.Column("conversation_id", sa.String(64), nullable=False, index=True),
        sa.Column("project_id", sa.String(64), nullable=True),
        sa.Column("creation_type", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default=_STATUS_DEFAULT),
        sa.Column("round", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("questions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("answers_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("requirements_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """删除 clarification_sessions（开发环境慎用）。"""
    bind = op.get_bind()
    if not _table_exists(bind):
        return
    op.drop_table(_TABLE)
