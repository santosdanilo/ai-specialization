from sec_filings_rag.ingestion.utils.semantic_chunker import Tokenizer


class SimpleChunker:
    """Splits text into token-bounded chunks without semantic clustering.

    The tokenizer is injected so chunking can be tested without transformers.
    """

    def __init__(self, tokenizer: Tokenizer, max_tokens: int = 300):
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


def load_simple_chunker(
    dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    max_tokens: int = 300,
) -> SimpleChunker:
    from transformers import AutoTokenizer

    return SimpleChunker(
        tokenizer=AutoTokenizer.from_pretrained(dense_model_name),
        max_tokens=max_tokens,
    )
