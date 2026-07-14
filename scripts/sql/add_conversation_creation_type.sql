-- 手动修复：conversations 表增加 creation_type
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS creation_type VARCHAR(16);
