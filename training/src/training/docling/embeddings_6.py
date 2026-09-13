from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from groq import Groq
import json


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 300

converter = DocumentConverter()

result = converter.convert("./2408.09869v5.pdf")

document = result.document

tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME),
    max_tokens=MAX_TOKENS,
)

chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=MAX_TOKENS,
    merge_peers=True,
)

chunks = list(chunker.chunk(document))
