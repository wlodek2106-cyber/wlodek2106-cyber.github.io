#!/usr/bin/env bash
# Restore only inside a newly created disposable local Docker container, never production.
set -euo pipefail
umask 077
archive="${1:?Supply encrypted .dump.gpg file}"
test -f "$archive"
command -v docker >/dev/null
command -v gpg >/dev/null
# Explicitly use a local Unix socket; do not use a remote Docker host/context.
unset DOCKER_HOST DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH
socket="${ACADEMY_LOCAL_DOCKER_SOCKET:-/var/run/docker.sock}"
[[ "$socket" = /* && -S "$socket" ]] || { echo "Local Docker socket required" >&2; exit 1; }
d(){ docker --host "unix://$socket" "$@"; }
# No exposed ports, no mounted volumes, no external network.
cid="$(d run -d --network none -e POSTGRES_HOST_AUTH_METHOD=trust postgres:17)"
trap 'd rm -fv "$cid" >/dev/null 2>&1 || true' EXIT
for i in $(seq 1 60); do
 if d exec "$cid" pg_isready -h 127.0.0.1 -U postgres >/dev/null 2>&1; then break; fi
 sleep 1
done
d exec "$cid" pg_isready -h 127.0.0.1 -U postgres >/dev/null
d exec "$cid" createdb -U postgres academy_restore
gpg --decrypt "$archive" | d exec -i "$cid" pg_restore --exit-on-error --no-owner --no-privileges -U postgres -d academy_restore
# Print aggregate counts only; never user data or credentials.
d exec "$cid" psql -v ON_ERROR_STOP=1 -U postgres -d academy_restore -c "SELECT (SELECT count(*) FROM academy.students) AS students,(SELECT count(*) FROM academy.enrollments) AS enrollments,(SELECT count(*) FROM academy.payment_invoices) AS invoices,(SELECT count(*) FROM academy.lesson_progress) AS completed_lessons;"
echo "Restore verified inside disposable local PostgreSQL 17 container. No production changes."
