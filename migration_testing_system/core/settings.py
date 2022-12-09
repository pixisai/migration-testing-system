from typing import Optional

from pydantic import BaseModel, BaseSettings, PostgresDsn


class EnvSettings(BaseSettings):
    postgres_dsn: Optional[PostgresDsn] = None

    migrations_folder: Optional[str] = None
    branch: Optional[str] = None

    log_level: str = "INFO"


env_settings = EnvSettings()


class Settings(BaseModel):
    postgres_dsn: PostgresDsn

    migrations_folder: Optional[str]
    branch: Optional[str]

    log_level: str
