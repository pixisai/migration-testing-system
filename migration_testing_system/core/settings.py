from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN: Optional[str] = None
    MIGRATIONS_FOLDER: Optional[str] = None


settings = Settings()
