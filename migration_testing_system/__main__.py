try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")


from argparse import ArgumentParser

from migration_testing_system.core.settings import Settings, env_settings


def _merge_vars(namespace1: object, namespace2: object) -> dict:
    return {
        **{
            k: v
            for k, v in [*vars(namespace1).items(), *vars(namespace2).items()]
            if v is not None
        }
    }


def parse_args(prog: str) -> Settings:

    parser = ArgumentParser(prog=prog)
    parser.add_argument(
        "-f",
        "--migrations-folder",
        type=str,
        help="Path to migration scripts",
    )
    parser.add_argument(
        "-d",
        "--postgres-dsn",
        type=str,
        help="Postgres DSN",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        help="Logging level",
    )
    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        help="Migrations brach to test",
    )
    parser.add_argument(
        "-F",
        "--dump-file",
        type=str,
        help="Dump file. Use s3:// prefix to download from S3 or file:// in local file system.",
    )

    namespace = parser.parse_args()

    return Settings.parse_obj(_merge_vars(env_settings, namespace))


if __name__ == "__main__":
    settings = parse_args(prog="migration_testing_system")

    from migration_testing_system import run

    run._run_testing(settings)
