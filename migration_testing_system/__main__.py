try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")


from alembic import command

# Тут надо будет создать объект Config, который будет содержать настройки для alembic
# Предполагается что это будут параметризованные настройки, пользователь сможет сам настроить пути к папке миграций
# Но можно установить дефолт на папку migrations
from alembic.config import Config
from alembic.script import ScriptDirectory

config = Config("alembic.ini")
# config = Config()
config.set_main_option("script_location", "alembic")
config.set_main_option(
    "sqlalchemy.url", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)
script = ScriptDirectory.from_config(config)


def current_revision(self):
    context.configure(connection=metadata.bind.connect(), transactional_ddl=True)
    migration_context = self.context.get_context()
    return migration_context.get_current_revision()


print("current revision->")
command.current(config)
""" Get & sort migrations, from first to last"""
revisions = list(script.walk_revisions("base", "heads"))
revisions.reverse()
print("---revisions---")
for revision in revisions:
    print(revision.revision)
    """command.upgrade(config, revision.revision)
    command.downgrade(config, revision.down_revision or '-1')
    command.upgrade(config, revision.revision)"""
