#!/bin/sh
# Chay migration truoc (tao/cap nhat bang), roi moi bat server.
set -e

echo "==> alembic upgrade head"
alembic upgrade head

echo "==> starting server"
exec "$@"
