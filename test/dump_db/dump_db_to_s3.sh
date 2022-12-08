S3_BUCKET_NAME='optimization-engine-migration-testing-system'
S3_KEY='db_dump.sql'

DB_HOST='localhost'
DB_PORT='5432'
DB_NAME='postgres'
DB_USER='postgres'
DB_DUMP_NAME='db_dump.sql'

pg_dump \
    --host=$DB_HOST \
    --port=$DB_PORT \
    --username=$DB_USER \
    --dbname=$DB_NAME > $DB_DUMP_NAME 


aws s3api put-object \
    --bucket $S3_BUCKET_NAME \
    --key $S3_KEY \
    --body $DB_DUMP_NAME \
    > /dev/null