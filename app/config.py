from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    default_provider: str = Field(default="openai", alias="BOOK_PRO_PROVIDER")
    default_model: str = Field(default="gpt-4.1-mini", alias="BOOK_PRO_MODEL")
    max_chapters_per_request: int | None = Field(default=None, alias="BOOK_PRO_MAX_CHAPTERS")
    output_dir: str = Field(default="books", alias="BOOK_PRO_OUTPUT_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
