import logging
import time
from typing import Optional

import docker
from pydantic import BaseSettings, PostgresDsn, validator

from migration_testing_system.run import run_testing


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
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
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db')}",
        )


settings = Settings()


def startup_postgres() -> None:
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


def check_postgres() -> bool:
    client = docker.from_env()
    container = client.containers.get(settings.container_name)
    return container.status == "running"


def shutdown_postgres() -> None:
    logging.info("Shutting down postgres container")
    client = docker.from_env()
    try:
        client.containers.get(settings.container_name).stop()
    except docker.errors.NotFound:
        pass
    logging.info("Postgres container stopped")


def valid_case():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_valid",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def invalid_case():
    startup_postgres()
    try:
        run_testing(
            settings.postgres_dsn,
            branch="versions_invalid",
            dump_file=settings.dump_file,
        )
    except Exception as e:
        print(e)

    shutdown_postgres()


def schema_drift_case():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_schema_drift",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def constraint_check():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_constraint_check_invalid",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def versions_check_nullable():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_check_nullable",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def versions_unique_constraints():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_unique_constraints",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def versions_primary_key():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_primary_key",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def versions_foreign_keys():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_foreign_keys",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def versions_unique_index():
    startup_postgres()
    run_testing(
        settings.postgres_dsn,
        branch="versions_unique_index",
        dump_file=settings.dump_file,
    )
    shutdown_postgres()


def run_test_cases():
    cases = [
        valid_case,
        invalid_case,
        schema_drift_case,
        constraint_check,
        versions_check_nullable,
        versions_unique_constraints,
        versions_primary_key,
        versions_foreign_keys,
        versions_unique_index,
    ]
    for case in cases:
        try:
            logging.info(f"Running case {case.__name__}")
            case()
            logging.info(f"Case {case.__name__} passed")
        except Exception as e:
            logging.error(f"Case {case.__name__} failed with error: {e}")

            if check_postgres():
                shutdown_postgres()

            exit(1)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s : %(name)s : %(message)s", level=logging.INFO
    )
    logging.root.name = "Testing"

    run_test_cases()
