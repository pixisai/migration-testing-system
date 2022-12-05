from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN: str
    MIGRATIONS_FOLDER: Optional[str] = None


settings = Settings()
