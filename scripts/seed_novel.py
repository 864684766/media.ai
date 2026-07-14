"""小说测试数据导入 CLI（默认 dry-run，--write 真实写库）。

【用途】
    将一段小说文本送入 Ingestion 流水线：
    - 默认 dry-run：只预览 chunk 切分结果，不写任何库
    - --write：写入 PG documents/chunks（真相源）+ Neo4j 图谱（若已配置）

【运行】
    poetry run python scripts/seed_novel.py --text "张三踏入青云宗..."
    poetry run python scripts/seed_novel.py --file ./chapter.txt
    poetry run python scripts/seed_novel.py --file ./chapter.txt --write

【前置条件（--write 模式）】
    .env 已配置 DATABASE_URL；已运行 scripts/init_postgres_tables.py 建表；
    可选配置 NEO4J_URI / NEO4J_PASSWORD 以同步写图谱与向量。
"""

import argparse
from pathlib import Path

from app.ingestion import IngestionDocument, run_ingestion_pipeline
from app.ingestion.adapter_factory import database_adapter_scope


def main() -> None:
    """解析 CLI 参数并执行导入（dry-run 或写库）。"""
    args = _parse_args()
    document = _build_document(args)
    if args.write:
        result = _run_write_mode(document)
    else:
        result = run_ingestion_pipeline(document, dry_run=True)
    _print_result(result)


def _run_write_mode(document: IngestionDocument):
    """--write 模式：真实写 PG（+ 可选 Neo4j）。"""
    with database_adapter_scope() as adapter:
        return run_ingestion_pipeline(document, adapter=adapter)


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="lanmo 小说文本导入（默认 dry-run）")
    parser.add_argument("--text", default="", help="直接传入的小说文本")
    parser.add_argument("--file", default="", help="文本文件路径")
    parser.add_argument("--document-id", default="novel-seed", help="文档 id")
    parser.add_argument("--project-id", default="default", help="项目 id")
    parser.add_argument("--write", action="store_true", help="真实写入 PG / Neo4j（默认只预览）")
    return parser.parse_args()


def _build_document(args: argparse.Namespace) -> IngestionDocument:
    """根据 CLI 参数构造 IngestionDocument。"""
    text = _read_input_text(args.text, args.file)
    return IngestionDocument(
        document_id=args.document_id,
        project_id=args.project_id,
        source=args.file or "cli-text",
        text=text,
    )


def _read_input_text(text: str, file_path: str) -> str:
    """读取 CLI 文本或文件内容。"""
    if text:
        return text
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return _default_seed_text()


def _default_seed_text() -> str:
    """返回默认测试文本。"""
    return "张三踏入青云宗，山门云雾翻涌。青云子立在石阶尽头，递给他一柄旧剑。"


def _print_result(result) -> None:
    """打印 dry-run 结果。"""
    print(f"document_id={result.document_id} chunk_count={result.chunk_count} dry_run={result.dry_run}")
    for chunk in result.chunks:
        print(f"[{chunk.chunk_id}] {chunk.text}")


if __name__ == "__main__":
    main()
