-- 手动修复：创建 clarification_sessions 表（PostgreSQL）
-- 适用：已有库缺表且无法立即 alembic upgrade 时
-- 等价于 alembic revision b7c8d9e0f1a2

CREATE TABLE IF NOT EXISTS clarification_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64),
    creation_type VARCHAR(16) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'collecting',
    round INTEGER NOT NULL DEFAULT 1,
    questions_json TEXT NOT NULL DEFAULT '[]',
    answers_json TEXT NOT NULL DEFAULT '[]',
    requirements_summary TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_clarification_sessions_conversation_id
    ON clarification_sessions (conversation_id);
