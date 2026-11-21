from typing import Any, Protocol


class Tokenizer(Protocol):
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]: ...


class Encoder(Protocol):
    max_seq_length: int

    def encode(self, texts: list[str], show_progress_bar: bool = False) -> Any: ...


class SemanticChunker:
    """Groups semantically similar paragraphs into token-bounded chunks.

    The encoder and tokenizer are injected so clustering logic can be tested
    without loading sentence-transformer models.
    """

    def __init__(
        self,
        encoder: Encoder,
        tokenizer: Tokenizer,
        clusterer_factory: Any,
        min_cluster_size: int = 3,
        orphan_cluster_size: int = 2,
        max_tokens: int = 300,
    ):
        self.model = encoder
        self.tokenizer = tokenizer
        self.min_cluster_size = min_cluster_size
        self.orphan_cluster_size = orphan_cluster_size
        self.max_tokens = max_tokens
        self._clusterer_factory = clusterer_factory

    def _cluster_and_process(self, texts, min_size):
        if len(texts) <= 1:
            return [], texts

        embeddings = self.model.encode(texts, show_progress_bar=False)
        labels = self._clusterer_factory(
            min_cluster_size=min_size, metric="euclidean"
        ).fit_predict(embeddings)

        from collections import defaultdict

        clusters = defaultdict(list)
        orphans = []
        for i, label in enumerate(labels):
            if label != -1:
                clusters[label].append(texts[i])
            else:
                orphans.append(texts[i])

        chunks = []
        for cluster_paras in clusters.values():
            current_chunk = []
            current_tokens = 0

            for para in cluster_paras:
                para_tokens = len(self.tokenizer.encode(para, add_special_tokens=False))

                if current_tokens + para_tokens > self.max_tokens and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [para]
                    current_tokens = para_tokens
                else:
                    current_chunk.append(para)
                    current_tokens += para_tokens

            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

        return chunks, orphans

    def create_chunks(self, text_content: str):
        paragraphs = [
            p.strip() for p in text_content.split("\n") if len(p.strip().split()) > 10
        ]
        if not paragraphs:
            return []

        final_chunks, orphans = self._cluster_and_process(
            paragraphs, self.min_cluster_size
        )

        if len(orphans) > 1:
            orphan_chunks, single_orphans = self._cluster_and_process(
                orphans, self.orphan_cluster_size
            )
            final_chunks.extend(orphan_chunks)
            final_chunks.extend(single_orphans)
        elif orphans:
            final_chunks.extend(orphans)

        return final_chunks


def load_semantic_chunker(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    max_tokens: int = 300,
) -> SemanticChunker:
    """Build a SemanticChunker with real (heavy) models loaded."""
    import hdbscan
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer

    model = SentenceTransformer(model_name)
    model.max_seq_length = 512
    return SemanticChunker(
        encoder=model,
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        clusterer_factory=hdbscan.HDBSCAN,
        max_tokens=max_tokens,
    )
