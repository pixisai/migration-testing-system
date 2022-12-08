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