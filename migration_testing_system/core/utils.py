import os
import shutil
from datetime import datetime
from os.path import exists

import boto3
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def download_file_from_s3(s3_bucket: str, s3_key: str, dest_file="dump.sql"):
    s3 = boto3.resource("s3")
    s3.Bucket(s3_bucket).download_file(Key=s3_key, Filename=dest_file)


def restore_db_from_dump(path_to_dump_file: str, engine: Engine) -> None:
    with engine.begin() as conn:
        with open(path_to_dump_file, "r") as f:
            conn.execute(f.read())


def restore_db(pg_dsn: str, path_to_file: str) -> None:
    engine: Engine = create_engine(pg_dsn)
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
    engine.dispose()


def make_new_file_name(file_name):
    filename, file_extension = os.path.splitext(file_name)
    now = datetime.now()
    timestamp = str(now.strftime("%Y%m%d_%H-%M-%S"))
    return filename + "_" + timestamp + file_extension


def dump_db(pg_url: str, dump_file: str):
    if exists(dump_file):
        shutil.move(dump_file, make_new_file_name(dump_file))
    os.system(
        f"pg_dump {pg_url} --schema='public' --schema='optimization' --exclude-table-data='optimization.*' > {dump_file}"
    )
