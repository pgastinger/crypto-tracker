#!/usr/bin/env sh
set -ex
#set -o errexit
#set -o pipefail
#set -o nounset

#until nc -w 1 -z db 5432; do
#  >&2 echo "Postgres is unavailable - sleeping"
#  sleep 1
#done
#sleep 2
#>&2 echo "Postgres is up - executing command"

until nc -w 1 -z redis-svc 6379; do
  >&2 echo "REDIS is unavailable - sleeping"
  sleep 1
done
sleep 2
>&2 echo "REDIS is up - executing command"

python /app/manage.py migrate --noinput
python /app/manage.py collectstatic --noinput
exec "$@"
