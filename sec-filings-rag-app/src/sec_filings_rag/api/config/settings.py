from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "google/gemma-4-31b-it:free"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=WORKSPACE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    qdrant_api_url: str = ""
    qdrant_api_key: str = ""
    collection_name: str = "financial"
    dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_model_name: str = "Qdrant/bm25"
    colbert_model_name: str = "colbert-ir/colbertv2.0"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = MODEL_NAME
    llm_fallback_models: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    edgar_client_email: str = ""
    vector_store_provider: str = "qdrant"


@lru_cache
def get_settings() -> Settings:
    return Settings()
