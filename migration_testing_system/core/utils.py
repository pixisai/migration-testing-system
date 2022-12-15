import boto3
from sqlalchemy.engine import Engine


def download_file_from_s3(s3_bucket: str, s3_key: str, dest_file="dump.sql"):
    s3 = boto3.resource("s3")
    s3.Bucket(s3_bucket).download_file(Key=s3_key, Filename=dest_file)


def restore_db_from_dump(path_to_dump_file: str, engine: Engine) -> None:
    with engine.connect() as conn:
        with open(path_to_dump_file, "r") as f:
            conn.execute(f.read())


# def restore_db_from_dump(db_host :str, db_port :str, db_username:str, db_name: str, dunmp_file: str) -> None:
#    os.system(f"psql --host {db_host} --port {db_port} --username {db_username} --dbname {db_name} -q -f {dunmp_file}")


def restore_db(path_to_file: str, engine: Engine) -> None:
    """ """
    if path_to_file.startswith("s3://"):
        dump_filename = "dump.sql"

        download_file_from_s3(
            *path_to_file[5:].split("/", maxsplit=1), dest_file=dump_filename
        )
        path_to_file = dump_filename

    elif path_to_file.startswith("file://"):
        path_to_file = path_to_file[7:]

    restore_db_from_dump(path_to_file, engine)
