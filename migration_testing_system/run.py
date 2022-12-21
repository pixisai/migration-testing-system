import logging
import os
import uuid
from contextlib import contextmanager

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


def _get_config(pg_url: str, migrations_folder: str) -> Config:
    alembic_ini_path = None
    if os.path.exists("alembic.ini"):
        alembic_ini_path = "alembic.ini"

    config = Config(alembic_ini_path)

    if migrations_folder is not None:
        config.set_main_option("script_location", migrations_folder)

    config.set_main_option("sqlalchemy.url", pg_url)

    return config


def _get_script_directory(config: Config) -> ScriptDirectory:
    script_directory = ScriptDirectory.from_config(config)

    return script_directory


def _get_current_revision(pg_dsn):
    with with_context(pg_dsn) as context:
        return context.get_current_revision()


def _test_revision(
    settings: Settings,
    revision: Script,
    tmp_dsn: str,
):
    config = _get_config(settings.postgres_dsn, settings.migrations_folder)
    upgrade(config, revision.revision)
    downgrade(config, "-1")
    result = compare(settings.postgres_dsn, tmp_dsn)
    logging.info(f"compare result.is_match = {result.is_match:} ")
    if not result.is_match:
        logging.info(f"Result not match. {result.errors}")


def _get_revisions(settings: Settings):
    branch = settings.branch
    branch_head = f"{branch}@head" if branch else "head"

    from_revision = _get_current_revision(settings.postgres_dsn)

    script_directory = _get_script_directory(
        _get_config(settings.postgres_dsn, settings.migrations_folder)
    )

    revisions = list(
        filter(
            lambda rev: from_revision != rev.revision,
            script_directory.walk_revisions(from_revision, branch_head),
        )
    )
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


def prepare_postgres_template(tmp_dsn, migrations_folder, revision):
    if revision is not None:
        config = _get_config(tmp_dsn, migrations_folder)
        upgrade(config, revision)


@contextmanager
def with_context(pg_dsn: str):
    engine = create_engine(pg_dsn)
    connection = engine.connect()
    context = MigrationContext.configure(connection)

    try:
        yield context
    finally:
        connection.close()
        engine.dispose()


def _run_testing(settings: Settings):
    restore_db(settings.postgres_dsn, settings.dump_file)

    revisions = _get_revisions(settings)
    tmp_rev = None

    with tmp_database(settings) as tmp_dsn:
        for revision in revisions:
            prepare_postgres_template(tmp_dsn, settings.migrations_folder, tmp_rev)
            tmp_rev = revision.revision
            _test_revision(settings, revision, tmp_dsn)


def get_db_name(pg_dsn: PostgresDsn):
    """get db name fom dsn"""
    db_name = pg_dsn.path
    if db_name[0] == "/":
        db_name = db_name[1:]
    return db_name


def run_testing(
    postgres_dsn: str,
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
    _run_testing(settings)
