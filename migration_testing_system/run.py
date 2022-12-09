import os
from typing import List

from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from sqlalchemy import create_engine

from migration_testing_system.core.settings import Settings
from migration_testing_system.core.utils import (
    download_file_from_s3,
    restore_db_from_dump,
)


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


def _walk_revisions(
    branch: str,
    config: Config,
    context: MigrationContext,
    script_directory: ScriptDirectory,
):
    branch_head = f"{branch}@head" if branch else "head"

    from_revision = context.get_current_revision()
    revisions: List[Script] = list(
        script_directory.walk_revisions(from_revision, branch_head)
    )

    revisions.reverse()

    _incremental_testing(config, context, from_revision, revisions)


def _run_testing(settings: Settings):
    engine = create_engine(settings.postgres_dsn)

    if settings.dump_file.startswith("s3://"):
        dump_filename = "dump.sql"

        download_file_from_s3(
            *settings.dump_file[5:].split("/", maxsplit=1), dest_file=dump_filename
        )
        settings.dump_file = dump_filename

    elif settings.dump_file.startswith("file://"):
        settings.dump_file = settings.dump_file[7:]

    restore_db_from_dump(settings.dump_file, engine)

    config = _get_config(settings)
    script_directory = _get_script_directory(config)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        _walk_revisions(
            settings.branch,
            config,
            context,
            script_directory,
        )


def run_testing(
    postgres_dsn: str,
    migrations_folder: str = "alembic",
    branch: str = "",
    log_level: str = "INFO",
    dump_file: str = "file://dump.sql",
):
    settings = Settings(
        postgres_dsn=postgres_dsn,
        migrations_folder=migrations_folder,
        branch=branch,
        log_level=log_level,
        dump_file=dump_file,
    )
    _run_testing(settings)
