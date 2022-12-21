from typing import Any, Dict, Optional

from pydantic import BaseModel, BaseSettings, PostgresDsn, validator


class EnvSettings(BaseSettings):
    POSTGRES_DRIVER: Optional[str] = "psycopg2"

    POSTGRES_HOST: Optional[str]
    POSTGRES_PORT: Optional[str]
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_DB: Optional[str]

    DB_SCHEMA: Optional[str] = "public"

    POSTGRES_URI: Optional[str] = None

    MIGRATIONS_FOLDER: Optional[str] = None
    BRANCH: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    DUMP_FILE: str = "dump.sql"

    @validator("POSTGRES_URI", pre=False)
    def _assemble_postgres_uri(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v

        if all(
            [
                user := values.get("POSTGRES_USER"),
                password := values.get("POSTGRES_PASSWORD"),
                postgres_host := values.get("POSTGRES_HOST"),
                postgres_port := values.get("POSTGRES_PORT"),
                postgres_db := values.get("POSTGRES_DB"),
            ]
        ):

            return PostgresDsn.build(
                scheme=f"postgresql",
                user=user,
                password=password,
                host=postgres_host,
                port=postgres_port,
                path=f"/{postgres_db}",
            )

        return None


class Settings(BaseModel):
    POSTGRES_URI: str

    DB_SCHEMA: str

    MIGRATIONS_FOLDER: str
    BRANCH: Optional[str]
    DUMP_FILE: str

    LOG_LEVEL: str
