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
from alembic.command import upgrade, downgrade

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
    parser.add_argument(
        "--POSTGRES_DSN",
        type=str,
        default=None,
        help="postgres DSN",
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

    if args.POSTGRES_DSN:
        settings.settings.POSTGRES_DSN = args.POSTGRES_DSN
        print("Set field POSTGRES_DSN from commandline args.")
    elif settings.settings.POSTGRES_DSN:
        print("Set field POSTGRES_DSN from envirenment variables.")
    else:
        settings.settings.POSTGRES_DSN = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
        print("Field POSTGRES_DSN is not configured. Set default value.")
    print(f"POSTGRES_DSN = {settings.settings.POSTGRES_DSN}")


init_settings()


config = Config("alembic.ini")

config.set_main_option("script_location", settings.settings.MIGRATIONS_FOLDER)
config.set_main_option("sqlalchemy.url", settings.settings.POSTGRES_DSN)

script = ScriptDirectory.from_config(config)


def get_current_revision(context):
    current_rev = context.get_current_revision()
    print(f"Current db rev: {current_rev}")
    return current_rev

def incremental_testing(context, from_revision, revisions):
    print("Incremental testing scripts.")
    print(revisions)
    for revision in revisions:
        if from_revision == revision.revision: continue
        print(f"For revision: {revision.revision}")
        with context.begin_transaction():
            upgrade(config, revision.revision)
            downgrade(config, "-1")
    print("Finished incremental test.")


def walk_revisions(context):
    from_revision = get_current_revision(context)
    revisions = list(script.walk_revisions(from_revision, "heads"))
    last_rev = revisions[0]
    revisions.reverse()

    incremental_testing(context, from_revision, revisions)
    print("downgrade to from_revision")
    downgrade(config, from_revision or "base")
    print("upgrade to last_revision")
    upgrade(config, last_rev.revision)


engine = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

with engine.connect() as connection:
    context = MigrationContext.configure(connection)
    walk_revisions(context)
