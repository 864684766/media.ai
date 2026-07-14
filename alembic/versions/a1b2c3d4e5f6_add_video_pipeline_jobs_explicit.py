"""add video_pipeline_jobs explicit

Revision ID: a1b2c3d4e5f6
Revises: f8a1c2b3d4e5
Create Date: 2026-07-10

【说明】
    增量迁移：显式创建 video_pipeline_jobs 表（已存在则跳过）。
    已有基线 create_all 的库可正常 upgrade；新库亦可通过本 revision 建表。
"""

from alembic import op
import sqlalchemy as sa

from app.storage.postgres import postgres_constants as pc

revision = "a1b2c3d4e5f6"
down_revision = "f8a1c2b3d4e5"
branch_labels = None
depends_on = None

_TABLE = pc.TABLE_VIDEO_PIPELINE_JOBS


def _table_exists(bind) -> bool:
    """检查表是否已存在。"""
    inspector = sa.inspect(bind)
    return _TABLE in inspector.get_table_names()


def upgrade() -> None:
    """创建 video_pipeline_jobs（checkfirst）。"""
    bind = op.get_bind()
    if _table_exists(bind):
        return
    op.create_table(
        _TABLE,
        sa.Column("job_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("state_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("error_message", sa.String(512), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """删除 video_pipeline_jobs（开发环境慎用）。"""
    bind = op.get_bind()
    if not _table_exists(bind):
        return
    op.drop_table(_TABLE)
