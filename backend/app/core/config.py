from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MedVision AI"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'medvision.db'}"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_path: str = str(ROOT_DIR / "models" / "best_model.pth")
    uploads_dir: str = str(ROOT_DIR / "uploads")
    artifacts_dir: str = str(ROOT_DIR / "artifacts")

    max_upload_mb: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
