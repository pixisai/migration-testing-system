try:
    pass
except ImportError:
    print("Alembic is not installed. Please install it with `pip install alembic`")


from argparse import ArgumentParser

from pydantic.error_wrappers import ValidationError

from migration_testing_system.core.settings import EnvSettings, Settings


def _keys_to_upper(d: dict) -> dict:
    return {k.upper(): v for k, v in d.items()}


def _remove_none_values(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def parse_args(prog: str) -> Settings:

    parser = ArgumentParser(prog=prog)

    full_uri_group = parser.add_argument_group(
        "Full URI. Mutually exclusive with 'URI parts'"
    )
    full_uri_group.add_argument(
        "--postgres-uri",
        type=str,
        help="Postgres URI",
    )

    separated_uri_group = parser.add_argument_group(
        "URI parts. Full URI will build automatically. "
        "Mutually exclusive with 'Full URI'"
    )
    separated_uri_group.add_argument(
        "--postgres-driver",
        type=str,
        help="Postgres driver",
    )
    separated_uri_group.add_argument(
        "--postgres-host",
        type=str,
        help="Postgres host",
    )
    separated_uri_group.add_argument(
        "--postgres-port",
        type=str,
        help="Postgres port",
    )
    separated_uri_group.add_argument(
        "--postgres-user",
        type=str,
        help="Postgres user",
    )
    separated_uri_group.add_argument(
        "--postgres-password",
        type=str,
        help="Postgres password",
    )
    separated_uri_group.add_argument(
        "--postgres-db",
        type=str,
        help="Postgres DB",
    )

    parser.add_argument(
        "-s",
        "--db-schema",
        type=str,
        help="DB schema",
    )
    parser.add_argument(
        "-f",
        "--migrations-folder",
        type=str,
        help="Path to migration scripts",
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

    separated_uri_group_args = [
        namespace.postgres_host,
        namespace.postgres_port,
        namespace.postgres_user,
        namespace.postgres_password,
        namespace.postgres_db,
    ]

    if namespace.postgres_uri and any(separated_uri_group_args):
        parser.error("Full URIs and Separated URIs are mutually exclusive")

    if any((namespace.postgres_uri, *separated_uri_group_args)) and (
        not namespace.postgres_uri or not all(separated_uri_group_args)
    ):
        parser.error("You must provide either Full URIs or Separated URIs")

    try:
        return Settings.parse_obj(
            EnvSettings(
                **_remove_none_values(
                    _keys_to_upper(
                        vars(namespace),
                    )
                )
            )
        )
    except ValidationError as e:
        print("Can't parse or build next parameters:")
        print("\n".join([e_ctx["loc"][0] for e_ctx in e.errors()]))
        parser.print_help()
        exit(-1)


if __name__ == "__main__":
    settings = parse_args(prog="migration_testing_system")

    from migration_testing_system import run

    run._run_testing(settings)
