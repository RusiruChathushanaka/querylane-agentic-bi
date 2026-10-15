import secrets
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Agentic BI"
    environment: Literal["local", "production", "test"] = "local"
    storage_backend: Literal["memory", "firestore"] = "memory"
    data_backend: Literal["fixture", "cloud"] = "fixture"
    ai_backend: Literal["fixture", "gemini"] = "fixture"
    google_cloud_project: str = "project-e8b1593d-009a-4822-abf"
    firestore_database: str = "agentic-bi-demo"
    bigquery_dataset: str = "agentic_bi_demo"
    bigquery_location: str = "asia-southeast1"
    text_model: str = "gemini-3.8-flash"
    text_model_location: str = "global"
    embedding_model: str = "gemini-embedding-001"
    embedding_location: str = "us-central1"
    embedding_dimensions: int = 768
    live_model: str = "gemini-live-2.5-flash-native-audio"
    live_model_location: str = "us-central1"
    cloud_sql_instance: str = ""
    postgres_dsn: str = ""
    postgres_database: str = "agentic_bi"
    postgres_user: str = "bi_reader"
    postgres_password: str = ""
    guest_signing_key: str = ""
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    guest_hourly_limit: int = 20
    workspace_daily_limit: int = 300
    voice_daily_limit: int = 30
    voice_max_seconds: int = 180
    bigquery_max_bytes: int = 1_073_741_824
    source_row_limit: int = 10_000
    source_byte_limit: int = 16_777_216
    fusion_row_limit: int = 50_000
    fusion_timeout_seconds: int = 10
    preview_rows: int = 1000
    query_timeout_seconds: int = 30
    analysis_timeout_seconds: int = 180
    lease_seconds: int = 45

    @property
    def origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.allowed_origins.split(",") if origin.strip()]

    def validate_runtime(self) -> None:
        if self.environment == "production":
            if (self.storage_backend, self.data_backend, self.ai_backend) != ("firestore", "cloud", "gemini"):
                raise ValueError(
                    "Production requires Firestore, cloud sources, and Gemini; fixtures are local only."
                )
            if len(self.guest_signing_key) < 32:
                raise ValueError("Production requires GUEST_SIGNING_KEY with at least 32 characters.")
            if not self.cloud_sql_instance and not self.postgres_dsn:
                raise ValueError("Configure CLOUD_SQL_INSTANCE or POSTGRES_DSN.")
        if not self.guest_signing_key:
            self.guest_signing_key = secrets.token_urlsafe(48)


@lru_cache
def get_settings() -> Settings:
    return Settings()
