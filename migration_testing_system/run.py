import logging
import os
import uuid
from contextlib import contextmanager
from typing import List

from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database
from sqlalchemydiff import compare

from migration_testing_system.core.settings import Settings
from migration_testing_system.core.utils import restore_db


def _get_config(settings: Settings) -> Config:
    alembic_ini_path = None
    if os.path.exists("alembic.ini"):
        alembic_ini_path = "alembic.ini"

    config = Config(alembic_ini_path)

    if settings.migrations_folder is not None:
        config.set_main_option("script_location", settings.migrations_folder)

    return config


def _get_script_directory(config: Config) -> ScriptDirectory:
    script_directory = ScriptDirectory.from_config(config)

    return script_directory


def _incremental_testing(
    config: Config,
    context: MigrationContext,
    from_revision: str,
    revisions: List[Script],
):
    for revision in revisions:
        if from_revision == revision.revision:
            continue

        with context.begin_transaction():
            upgrade(config, revision.revision)
            downgrade(config, "-1")


def _get_revisions(
    branch: str,
    from_revision,
    script_directory: ScriptDirectory,
):
    branch_head = f"{branch}@head" if branch else "head"

    revisions = list(script_directory.walk_revisions(from_revision, branch_head))
    revisions.reverse()
    return revisions


@contextmanager
def tmp_database(settings: Settings):
    pg_dsn: PostgresDsn = settings.postgres_dsn
    tmp_dsn: str = "_".join([str(pg_dsn), uuid.uuid4().hex])

    create_database(tmp_dsn, template=get_db_name(pg_dsn))
    logging.info(f"created template database:'{tmp_dsn}'")
    try:
        yield tmp_dsn
    finally:
        drop_database(tmp_dsn)
        logging.info(f"drop database:'{tmp_dsn}'")


def _run_testing(settings: Settings, check_schema_drift: bool = False):
    restore_db(settings.postgres_dsn, settings.dump_file)

    if check_schema_drift:
        logging.info("schema drift testitng")
        with tmp_database(settings) as tmp_dsn:
            _migration_testing(settings)
            result = compare(str(settings.postgres_dsn), tmp_dsn)
            logging.info(f"compare result.is_match = {result.is_match:} ")
            if not result.is_match:
                logging.info(f"Result not match. {result.errors}")
    else:
        _migration_testing(settings)


def _migration_testing(settings: Settings):
    engine = create_engine(settings.postgres_dsn)

    config = _get_config(settings)
    script_directory = _get_script_directory(config)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        from_revision = context.get_current_revision()

        revisions = _get_revisions(
            settings.branch,
            from_revision,
            script_directory,
        )

        _incremental_testing(config, context, from_revision, revisions)
        downgrade(config, from_revision)


def get_db_name(pg_dsn: PostgresDsn):
    """get db name fom dsn"""
    db_name = pg_dsn.path
    if db_name[0] == "/":
        db_name = db_name[1:]
    return db_name


def run_testing(
    postgres_dsn: str,
    check_schema_drift: bool = False,
    migrations_folder: str = "alembic",
    branch: str = "",
    log_level: str = "INFO",
    dump_file: str = "file://dump.sql",
):
    settings = Settings(
        postgres_dsn=postgres_dsn,
        branch=branch,
        migrations_folder=migrations_folder,
        log_level=log_level,
        dump_file=dump_file,
    )
    _run_testing(settings, check_schema_drift)
