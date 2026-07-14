"""Ingestion Lite 单元测试。"""

from app.ingestion import IngestionDocument, chunk_document, run_ingestion_pipeline
from app.ingestion.ingestion_settings import load_ingestion_settings
from scripts.seed_novel import _default_seed_text


def test_load_ingestion_settings_from_yaml() -> None:
    """应从 yaml 字典读取 ingestion 配置。"""
    settings = load_ingestion_settings(
        {
            "ingestion": {
                "chunk_size": 10,
                "chunk_overlap": 2,
                "dry_run_default": True,
            }
        }
    )
    assert settings["chunk_size"] == 10
    assert settings["chunk_overlap"] == 2
    assert settings["dry_run_default"] is True


def test_chunk_document_with_overlap() -> None:
    """chunker 应按固定窗口和 overlap 切分文本。"""
    document = IngestionDocument(document_id="doc-1", text="abcdefghij")
    chunks = chunk_document(document, chunk_size=4, chunk_overlap=1)
    assert [chunk.text for chunk in chunks] == ["abcd", "defg", "ghij", "j"]
    assert chunks[0].chunk_id == "doc-1:0"


def test_run_ingestion_pipeline_dry_run() -> None:
    """pipeline 应返回 dry-run 结果且不写远程库。"""
    document = IngestionDocument(document_id="doc-2", text="张三进入青云宗。")
    result = run_ingestion_pipeline(document, dry_run=True)
    assert result.document_id == "doc-2"
    assert result.dry_run is True
    assert result.chunk_count >= 1


def test_seed_novel_default_text() -> None:
    """seed_novel 默认文本应包含测试主角。"""
    assert "张三" in _default_seed_text()
