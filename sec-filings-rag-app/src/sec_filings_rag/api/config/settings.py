from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    qdrant_api_url: str
    qdrant_api_key: str
    collection_name: str = "financial"
    dense_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_model_name = "Qdrant/bm25"
    colbert_model_name = "colbert-ir/colbertv2.0"


settings = Settings()
