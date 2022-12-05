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
from sqlalchemy import engine_from_config, pool
from test_project.models import metadata

target_metadata = metadata
config = Config("alembic.ini")

config.set_main_option(
    "script_location",
    "/Users/denis/Documents/dev/pixisai/migration-testing-system/test/alembic",
)
config.set_main_option(
    "sqlalchemy.url", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)

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
        print(f"current db rev: {current_rev}")
    return current_rev


def step(revision):
    print(f"step->:{revision}")
    """ command.upgrade(config, revision.revision)
        command.downgrade(config, revision.down_revision or '-1')
        command.upgrade(config, revision.revision)"""


def walk_revisions(from_revision):
    revisions = list(script.walk_revisions(from_revision, "heads"))
    revisions.reverse()

    rev_accum = list()

    for revision in revisions:
        if from_revision == revision.revision:
            continue
        print(f"for script revision: {revision.revision}")
        rev_accum.append(revision.revision)
        for rev in rev_accum:
            step(rev)


walk_revisions(get_current_revision())
