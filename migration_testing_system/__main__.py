try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")


# Тут надо будет создать объект Config, который будет содержать настройки для alembic
# Предполагается что это будут параметризованные настройки, пользователь сможет сам настроить пути к папке миграций
# Но можно установить дефолт на папку migrations
