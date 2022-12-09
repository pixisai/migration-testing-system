import subprocess

import boto3

"""
Example script for splitting argumets for subbrocess.

import shlex, subprocess
command_line = "psql --host $DB_HOST \
    --port $DB_PORT  \
    --username $DB_USER \
    --dbname $DB_NAME \
    -q -f $DB_DUMP_NAME"
args = shlex.split(command_line)
print(args)

output: ['psql', '--host', '$DB_HOST', '--port', '$DB_PORT', '--username', '$DB_USER', '--dbname', '$DB_NAME', '-q', '-f', '$DB_DUMP_NAME']
"""

"""

docker-compose up -d

S3_BUCKET_NAME='optimization-engine-migration-testing-system'
S3_KEY='db_dump.sql'

DB_HOST='localhost'
DB_PORT='5432'
DB_NAME='postgres'
DB_USER='postgres'
DB_DUMP_NAME='db_dump_from_s3.sql'

aws s3api get-object \
    --bucket $S3_BUCKET_NAME \
    --key $S3_KEY \
    $DB_DUMP_NAME > /dev/null

psql --host $DB_HOST \
    --port $DB_PORT  \
    --username $DB_USER \
    --dbname $DB_NAME \
    -q -f $DB_DUMP_NAME

python3 -m migration_testing_system --MIGRATIONS_FOLDER=/Users/denis/Documents/dev/pixisai/migration-testing-system/test/alembic

docker-compose down --volumes

"""


def download_file_from_s3(
    s3_bucket="optimization-engine-migration-testing-system",
    s3_key="db_dump.sql",
    path_to_dest_file="db_dump_from_s3.sql",
):
    s3 = boto3.resource("s3")
    s3.Bucket(s3_bucket).download_file(key=s3_key, Filename=path_to_dest_file)


def restore_db_from_dump(
    path_to_dump_file,
    db_host="localhost",
    db_port="5432",
    user_name="postgres",
    db_name="postgres",
):
    subprocess.run(
        [
            "psql",
            "--host",
            db_host,
            "--port",
            db_port,
            "--username",
            user_name,
            "--dbname",
            db_name,
            "-q",
            "-f",
            path_to_dump_file,
        ],
        capture_output=True,
    )
