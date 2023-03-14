#!/bin/sh
# echo 'check'
# if [ "$PG_DB" = "app" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $PG_HOST $PG_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

PYTHONUNBUFFERED=TRUE  gunicorn app:get_app --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker --capture-output

# exec "$@"
