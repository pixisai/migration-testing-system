import boto3
from sqlalchemy.engine import Engine


def download_file_from_s3(s3_bucket: str, s3_key: str, dest_file="dump.sql"):
    s3 = boto3.resource("s3")
    s3.Bucket(s3_bucket).download_file(Key=s3_key, Filename=dest_file)


def restore_db_from_dump(path_to_dump_file: str, engine: Engine) -> None:
    with engine.connect() as conn:
        with open(path_to_dump_file, "r") as f:
            conn.execute(f.read())
