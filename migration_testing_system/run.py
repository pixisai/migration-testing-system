import os
from typing import Callable, List

from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from sqlalchemy import create_engine

from migration_testing_system.core.settings import Settings


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


def _run_testing(settings: Settings, logging_callback: Callable = None):
    engine = create_engine(settings.postgres_dsn)
    config = _get_config(settings)
    script_directory = _get_script_directory(config)

    if logging_callback:
        logging_callback()

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
    logging_callback: Callable = None,
):
    settings = Settings(
        postgres_dsn=postgres_dsn,
        migrations_folder=migrations_folder,
        branch=branch,
        log_level=log_level,
    )
    _run_testing(settings, logging_callback=logging_callback)
