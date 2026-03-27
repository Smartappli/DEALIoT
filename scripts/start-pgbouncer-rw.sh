#!/bin/sh
set -eu
export DB_PASSWORD="$(cat /run/secrets/app_user_password)"
exec /entrypoint.sh pgbouncer /etc/pgbouncer/pgbouncer.ini
