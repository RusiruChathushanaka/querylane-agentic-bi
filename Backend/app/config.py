import secrets
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Agentic BI"
    environment: Literal["local", "production", "test"] = "local"
    storage_backend: Literal["memory", "firestore"] = "memory"
    data_backend: Literal["fixture", "cloud"] = "fixture"
    data_profile: Literal["legacy", "timeseries"] = "legacy"
    retail_bundle_path: str = ""
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
    skill_catalog_limit: int = 100
    dashboard_limit: int = Field(default=100, ge=1, le=1000)
    dashboard_item_limit: int = Field(default=20, ge=1, le=20)
    dashboard_guest_hourly_limit: int = Field(default=50, ge=1)
    dashboard_workspace_daily_limit: int = Field(default=300, ge=1)
    dashboard_recovery_days: int = Field(default=30, ge=1, le=365)
    skill_guest_hourly_limit: int = 20
    skill_workspace_daily_limit: int = 100
    author_guest_hourly_limit: int = 3
    author_workspace_daily_limit: int = 12
    author_voice_guest_hourly_limit: int = 6
    author_voice_workspace_daily_limit: int = 30
    author_voice_max_seconds: int = 600
    author_lifetime_seconds: int = 21600
    author_turn_limit: int = 24
    author_tool_limit: int = 48
    author_update_limit: int = 24
    author_transcript_bytes: int = 65536
    report_catalog_limit: int = Field(default=100, ge=1, le=1000)
    reports_enabled: bool = True
    report_dispatch: Literal["local", "cloud_tasks", "disabled"] = "local"
    report_worker_url: str = ""
    report_queue: str = "agentic-bi-reports"
    report_region: str = "asia-southeast1"
    report_dispatch_service_account: str = ""
    report_bucket: str = ""
    report_local_directory: str = ".reports"
    report_guest_daily_limit: int = Field(default=3, ge=1)
    report_workspace_daily_limit: int = Field(default=12, ge=1)
    report_concurrency: int = Field(default=2, ge=1, le=2)
    report_timeout_seconds: int = Field(default=600, ge=10, le=600)
    report_model_calls: int = Field(default=24, ge=1, le=24)
    report_output_tokens: int = Field(default=32000, ge=1000, le=32000)
    report_query_limit: int = Field(default=12, ge=1, le=12)
    report_scan_bytes: int = Field(default=8589934592, ge=1)
    report_fit_limit: int = Field(default=64, ge=1, le=64)
    report_fit_seconds: int = Field(default=120, ge=1, le=120)
    planning_enabled: bool = True
    forecast_plan_fit_limit: int = Field(default=128, ge=1, le=128)
    report_research_enabled: bool = False
    report_timesfm_enabled: bool = False
    report_timesfm_verified: bool = False
    report_timesfm_targets: int = Field(default=2, ge=1, le=2)
    report_timesfm_jobs: int = Field(default=4, ge=1, le=4)
    report_timesfm_job_seconds: int = Field(default=45, ge=1, le=45)
    report_timesfm_seconds: int = Field(default=120, ge=1, le=120)
    report_timesfm_input_tokens: int = Field(default=100000, ge=1, le=100000)
    report_timesfm_output_tokens: int = Field(default=10000, ge=1, le=10000)

    @property
    def origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def postgres_schema(self) -> str:
        return "retail_timeseries" if self.data_profile == "timeseries" else "retail"

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
            if self.reports_enabled and self.report_dispatch == "local":
                raise ValueError("Production reports require cloud_tasks dispatch or must be disabled.")
            if (
                self.reports_enabled
                and self.report_dispatch == "cloud_tasks"
                and not all(
                    (self.report_worker_url, self.report_dispatch_service_account, self.report_bucket)
                )
            ):
                raise ValueError("Reports require worker URL, dispatch identity, and private export bucket.")
        if not self.guest_signing_key:
            self.guest_signing_key = secrets.token_urlsafe(48)


@lru_cache
def get_settings() -> Settings:
    return Settings()
