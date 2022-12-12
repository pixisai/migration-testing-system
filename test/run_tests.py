import logging
import time
from typing import Optional

import docker
from pydantic import BaseSettings, PostgresDsn, validator

from migration_testing_system.run import run_testing


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "postgres"

    postgres_dsn: Optional[str] = None

    container_name: str = "test_postgres"
    dump_file: str = "file://dump.sql"

    @validator("postgres_dsn", pre=False)
    def build_postgres_dsn(cls, v, values):
        if v is not None:
            return v

        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            path=f"/{values.get('postgres_db')}",
        )


settings = Settings()


def startup_postgres(settings) -> None:
    logging.info("Starting postgres container")

    client = docker.from_env()
    container = client.containers.run(
        "postgres:13.4-alpine",
        auto_remove=True,
        detach=True,
        ports={"5432": settings.postgres_port},
        environment={
            "POSTGRES_PASSWORD": settings.postgres_password,
            "POSTGRES_USER": settings.postgres_user,
            "POSTGRES_DB": settings.postgres_db,
        },
        name=settings.container_name,
    )

    for log in container.logs(stream=True):
        if "database system is ready to accept connections" in log.decode():
            break
    time.sleep(1)

    logging.info("Postgres container started")


def check_postgres(container_name) -> bool:
    client = docker.from_env()
    container = client.containers.get(container_name)
    return container.status == "running"


def shutdown_postgres(container_name) -> None:
    logging.info("Shutting down postgres container")
    client = docker.from_env()
    try:
        client.containers.get(container_name).stop()
    except docker.errors.NotFound:
        pass
    logging.info("Postgres container stopped")


def valid_case():
    startup_postgres(settings)
    run_testing(
        settings.postgres_dsn,
        branch="versions_valid",
        dump_file=settings.dump_file,
    )
    shutdown_postgres(settings.container_name)


def invalid_case():
    startup_postgres(settings)
    try:
        run_testing(
            settings.postgres_dsn,
            branch="versions_invalid",
            dump_file=settings.dump_file,
        )
    except Exception as e:
        print(e)

    shutdown_postgres(settings.container_name)


def copy_settings(settings):
    settings_ref_db = settings.copy()
    settings_ref_db.postgres_port = settings_ref_db.postgres_port + 1
    settings_ref_db.postgres_dsn = None


def run_schema_drift_testing():
    pass


def schema_drift_case():
    """Copy setting for create refernece db."""
    settings_ref_db = copy_settings(settings)
    startup_postgres(settings)
    startup_postgres(settings_ref_db)

    run_schema_drift_testing()

    shutdown_postgres(settings.container_name)
    shutdown_postgres(settings_ref_db.container_name)


def run_test_cases():
    cases = [valid_case, invalid_case]
    for case in cases:
        try:
            logging.info(f"Running case {case.__name__}")
            case()
            logging.info(f"Case {case.__name__} passed")
        except Exception as e:
            logging.error(f"Case {case.__name__} failed with error: {e}")

            if check_postgres(settings.container_name):
                shutdown_postgres(settings.container_name)

            exit(1)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s : %(name)s : %(message)s", level=logging.INFO
    )
    logging.root.name = "Testing"

    run_test_cases()
