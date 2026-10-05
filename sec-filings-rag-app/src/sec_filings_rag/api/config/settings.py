from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "openai/gpt-oss-120b"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=WORKSPACE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    qdrant_api_url: str
    qdrant_api_key: str
    collection_name: str = "financial"
    dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_model_name: str = "Qdrant/bm25"
    colbert_model_name: str = "colbert-ir/colbertv2.0"
    groq_api_key: str
    groq_model: str = MODEL_NAME


settings = Settings()
