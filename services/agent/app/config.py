from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://rm:rm_dev_password@localhost:5432/rm_copilot"

    llm_provider: str = "mock"  # mock | anthropic | openai
    llm_model: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""
    # USD per million tokens, for models missing from app.llm.pricing.PRICES.
    llm_price_input_per_mtok: float | None = None
    llm_price_output_per_mtok: float | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
