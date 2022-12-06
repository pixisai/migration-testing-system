export PG_USERNAME=$(aws secretsmanager get-secret-value --secret-id dev/rds/optimization --query SecretString --output text | jq --raw-output '.username')
export PG_PASSWORD=$(aws secretsmanager get-secret-value --secret-id dev/rds/optimization --query SecretString --output text | jq --raw-output '.password')

pg_dump --host=optimization-engine-dev.c3papx4hi2vl.ap-south-1.rds.amazonaws.com --port=5432 --username=$PG_USERNAME --password --dbname=optimization_dev_pse --schema='public' --schema='optimization' --exclude-table-data='optimization.*' > db.sql
