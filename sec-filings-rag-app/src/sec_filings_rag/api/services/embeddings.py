from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding

from sec_filings_rag.api.config.settings import settings


class EmbeddingService:
    def __init__(self):
        self.dense_model = TextEmbedding(settings.dense_model_name)
        self.sparse_model = SparseTextEmbedding(settings.sparse_model_name)
        self.colbert_model = LateInteractionTextEmbedding(settings.colbert_model_name)

    def embedded_query(self, query: str):
        query_dense_embedding = next(
            iter(self.dense_model.query_embed([query]))
        ).tolist()

        query_sparse_embedding = next(
            iter(self.sparse_model.query_embed([query]))
        ).as_object()

        query_colbert_embedding = next(
            iter(self.colbert_model.query_embed([query]))
        ).tolist()

        return query_dense_embedding, query_sparse_embedding, query_colbert_embedding
