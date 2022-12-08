docker-compose up -d
sh ./dump_db/restore_db_from_s3.sh
python3 -m migration_testing_system --MIGRATIONS_FOLDER=/Users/denis/Documents/dev/pixisai/migration-testing-system/test/alembic
docker-compose down --volumes