export PG_USERNAME=$(aws secretsmanager get-secret-value --secret-id dev/rds/optimization --query SecretString --output text | jq --raw-output '.username')
export PG_PASSWORD=$(aws secretsmanager get-secret-value --secret-id dev/rds/optimization --query SecretString --output text | jq --raw-output '.password')


pg_dump \
    --host=$DB_HOST \
    --port=$DB_PORT \
    --username=$DB_USER \
    --dbname=$DB_NAME
    --schema='public'
    --schema='optimization'
     --exclude-table-data='optimization.*' >db.sql
