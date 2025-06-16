#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

echo "Attempting to connect to PostgreSQL at $host..."
echo "Using password: $DB_PASSWORD"
echo "Using user: postgres"
echo "Host: $host"

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

# Create database if it doesn't exist
PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "postgres" -c "CREATE DATABASE $DB_NAME"

>&2 echo "Postgres is up - executing command"
exec $cmd 