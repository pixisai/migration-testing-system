try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")

# Тут надо будет создать объект Config, который будет содержать настройки для alembic®
# Предполагается что это будут параметризованные настройки, пользователь сможет сам настроить пути к папке миграций
# Но можно установить дефолт на папку migrations

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from configargparse import ArgumentParser
from sqlalchemy import engine_from_config, pool

from migration_testing_system.core import settings


def init_settings():
    print("Start initiating systems settings.")
    parser = ArgumentParser()
    parser.add_argument(
        "--MIGRATIONS_FOLDER",
        type=str,
        default=None,
        help="path to migration scripts",
        required=False,
    )
    args = parser.parse_args()

    if args.MIGRATIONS_FOLDER:
        settings.settings.MIGRATIONS_FOLDER = args.MIGRATIONS_FOLDER
        print("Set field MIGRATIONS_FOLDER from commandline args.")
    elif settings.settings.MIGRATIONS_FOLDER:
        print("Set field MIGRATIONS_FOLDER from envirenment variables.")
    else:
        print("Field MIGRATIONS_FOLDER is not configured.")
    print(f"MIGRATIONS_FOLDER = {settings.settings.MIGRATIONS_FOLDER}")
    print("Set field POSTGRES_DSN from envirenment variables.")
    print(f"POSTGRES_DSN = {settings.settings.POSTGRES_DSN}")


init_settings()


config = Config("alembic.ini")

config.set_main_option("script_location", settings.settings.MIGRATIONS_FOLDER)
config.set_main_option("sqlalchemy.url", settings.settings.POSTGRES_DSN)

script = ScriptDirectory.from_config(config)


def get_current_revision():
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        print(f"Current db rev: {current_rev}")
    return current_rev


def step(revision):
    print(f"step->:{revision.revision}")
    """ command.upgrade(config, revision.revision)
        command.downgrade(config, revision.down_revision or '-1')
        command.upgrade(config, revision.revision)"""


def walk_revisions(from_revision):
    print("Preparing list of revisions for upgrade.")
    revisions = list(script.walk_revisions(from_revision, "heads"))
    revisions.reverse()

    rev_accum = list()

    for revision in revisions:
        if from_revision == revision.revision:
            continue
        print(f"for script revision: {revision.revision}")
        rev_accum.append(revision)
        for rev in rev_accum:
            step(rev)


walk_revisions(get_current_revision())
