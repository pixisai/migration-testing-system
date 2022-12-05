try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")

from alembic.migration import MigrationContext

# Тут надо будет создать объект Config, который будет содержать настройки для alembic
# Предполагается что это будут параметризованные настройки, пользователь сможет сам настроить пути к папке миграций
# Но можно установить дефолт на папку migrations
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

config = Config("alembic.ini")

config.set_main_option("script_location", "/Users/denis/Documents/dev/pixisai/migration-testing-system/test/alembic")

script = ScriptDirectory.from_config(config)

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
conn = engine.connect()
context = MigrationContext.configure(conn)

current_rev = context.get_current_revision()
print(f"current rev: {current_rev}")

revisions = script.walk_revisions(current_rev, "heads")

print("---revisions---")
for revision in revisions:
    if current_rev != revision.revision:
        print(revision.revision)
        """command.upgrade(config, revision.revision)
        command.downgrade(config, revision.down_revision or '-1')
        command.upgrade(config, revision.revision)"""
