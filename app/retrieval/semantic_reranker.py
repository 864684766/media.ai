"""语义 Rerank（Embedder 余弦相似度，Cross-Encoder 轻量替代）。"""

from app.utils.cosine_similarity_helper import cosine_similarity
from app.ingestion.embedder import Embedder
from app.retrieval.retrieval_models import RetrievedChunk


class SemanticReranker:
    """基于 embedding 余弦相似度的精排器。"""

    def __init__(self, embedder: Embedder) -> None:
        """绑定 embedder。"""
        self._embedder = embedder

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        """语义精排。"""
        if not chunks:
            return []
        vectors = self._embed_texts(question, chunks)
        rescored = self._score_chunks(chunks, vectors)
        rescored.sort(key=lambda chunk: chunk.score, reverse=True)
        return rescored[:top_k]

    def _embed_texts(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> tuple[list[float], list[list[float]]]:
        """向量化问题与证据。"""
        texts = [question] + [chunk.text for chunk in chunks]
        vectors = self._embedder.embed_texts(texts)
        return vectors[0], vectors[1:]

    def _score_chunks(
        self,
        chunks: list[RetrievedChunk],
        vectors: tuple[list[float], list[list[float]]],
    ) -> list[RetrievedChunk]:
        """计算语义分。"""
        query_vec, chunk_vecs = vectors
        rescored: list[RetrievedChunk] = []
        for chunk, vec in zip(chunks, chunk_vecs):
            score = cosine_similarity(query_vec, vec) + chunk.score * 0.1
            rescored.append(chunk.model_copy(update={"score": score}))
        return rescored
