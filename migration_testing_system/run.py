import logging
import os
import uuid
from contextlib import contextmanager

from alembic import context
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from sqlalchemy import create_engine, engine_from_config, pool
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


def _get_current_revision(pg_dsn):
    with with_context(pg_dsn) as context:
        return context.get_current_revision()


def _test_revision(
    settings: Settings,
    revision: Script,
    tmp_dsn: str,
):
    config = _get_config(settings.POSTGRES_URI, settings.MIGRATIONS_FOLDER)
    _upgrade(config, revision.revision)
    _downgrade(config, "-1")
    result = compare(settings.POSTGRES_URI, tmp_dsn)
    logging.info(f"compare result.is_match = {result.is_match:} ")
    if not result.is_match:
        logging.info(f"Result not match. {result.errors}")


def _get_revisions(settings: Settings):
    branch = settings.BRANCH
    branch_head = f"{branch}@head" if branch else "head"

    from_revision = _get_current_revision(settings.POSTGRES_URI)

    config = _get_config(settings.POSTGRES_URI, settings.MIGRATIONS_FOLDER)
    script = ScriptDirectory.from_config(config)

    revisions = list(
        filter(
            lambda rev: from_revision != rev.revision,
            script.walk_revisions(from_revision, branch_head),
        )
    )
    revisions.reverse()

    return revisions


@contextmanager
def tmp_database(settings: Settings):
    sqlalchemy_uri = settings.POSTGRES_URI
    tmp_uri: str = "_".join([str(sqlalchemy_uri), uuid.uuid4().hex])
    create_database(tmp_uri, template=get_db_name(sqlalchemy_uri))
    logging.info(f"created template database:'{tmp_uri}'")
    try:
        yield tmp_uri
    finally:
        drop_database(tmp_uri)
        logging.info(f"drop database:'{tmp_uri}'")


def prepare_postgres_template(tmp_dsn, migrations_folder, revision):
    if revision is not None:
        config = _get_config(tmp_dsn, migrations_folder)
        _upgrade(config, revision)


def _upgrade(
    config: Config,
    revision: str,
) -> None:
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs(revision, rev)

    with EnvironmentContext(
        config,
        script,
        fn=upgrade,
        destination_rev=revision,
    ):
        run_migrations_online(config)


def _downgrade(
    config: Config,
    revision: str,
) -> None:
    script = ScriptDirectory.from_config(config)

    def downgrade(rev, context):
        return script._downgrade_revs(revision, rev)

    with EnvironmentContext(
        config,
        script,
        fn=downgrade,
        destination_rev=revision,
    ):
        run_migrations_online(config)


def run_migrations_online(config) -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


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
    restore_db(settings.POSTGRES_URI, settings.DUMP_FILE)

    revisions = _get_revisions(settings)
    tmp_rev = None

    with tmp_database(settings) as tmp_dsn:
        for revision in revisions:
            prepare_postgres_template(tmp_dsn, settings.MIGRATIONS_FOLDER, tmp_rev)
            tmp_rev = revision.revision
            _test_revision(settings, revision, tmp_dsn)


def get_db_name(db_uri: str) -> str:
    return db_uri.split("/")[-1]


def run_testing(
    postgres_uri: str,
    migrations_folder: str = "alembic",
    branch: str = "",
    db_schema: str = "public",
    log_level: str = "INFO",
    dump_file: str = "file://dump.sql",
):
    settings = Settings(
        POSTGRES_URI=postgres_uri,
        BRANCH=branch,
        MIGRATIONS_FOLDER=migrations_folder,
        LOG_LEVEL=log_level,
        DUMP_FILE=dump_file,
        DB_SCHEMA=db_schema,
    )
    _run_testing(settings)
