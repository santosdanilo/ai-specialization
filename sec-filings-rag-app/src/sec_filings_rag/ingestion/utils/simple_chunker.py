from sec_filings_rag.ingestion.utils.semantic_chunker import Tokenizer


class SimpleChunker:
    """Splits text into token-bounded chunks without semantic clustering.

    The tokenizer is injected so chunking can be tested without transformers.
    """

    def __init__(self, tokenizer: Tokenizer, max_tokens: int):
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer

    def create_chunks(self, text_content: str):
        paragraphs = [p.strip() for p in text_content.split("\n") if p.split()]

        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
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

        return chunks


def load_simple_chunker(settings) -> SimpleChunker:
    """Build a SimpleChunker with the real tokenizer loaded.

    Reads the model name and chunk token budget from ``settings`` so they
    stay colocated with the embedder config.
    """
    from transformers import AutoTokenizer

    return SimpleChunker(
        tokenizer=AutoTokenizer.from_pretrained(settings.dense_model_name),
        max_tokens=settings.chunk_max_tokens,
    )
