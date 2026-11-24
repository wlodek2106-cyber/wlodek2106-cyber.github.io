#!/usr/bin/env bash
# Local operator only. Requires pg_dump and GnuPG; no secrets in repository.
set -euo pipefail
umask 077
: "${ACADEMY_DATABASE_URL:?Set the direct Academy DB connection in your local shell}"
command -v pg_dump >/dev/null
command -v gpg >/dev/null
outdir="${1:-$HOME/zer0life-academy-backups}"
mkdir -p "$outdir"
# Reject symlinked destination and broad existing directory permissions where possible.
if [[ -L "$outdir" ]]; then echo "Refusing symlink destination" >&2; exit 1; fi
chmod 700 "$outdir"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$outdir/academy-$stamp.dump.gpg"
tmp="$(mktemp "$outdir/.academy-XXXXXX")"
trap 'rm -f "$tmp"' EXIT
[[ ! -e "$out" ]] || { echo "Backup already exists" >&2; exit 1; }
# URI in process environment, not command arguments; pg_dump snapshot, Academy schema only.
# GPG prompts locally for passphrase. No plaintext archive written.
PGDATABASE="$ACADEMY_DATABASE_URL" PGCONNECT_TIMEOUT=10 pg_dump --schema=academy --format=custom --no-owner --no-privileges --no-password |
  gpg --symmetric --cipher-algo AES256 --output - > "$tmp"
test -s "$tmp"
mv "$tmp" "$out"
if command -v sha256sum >/dev/null; then (cd "$outdir" && sha256sum "$(basename "$out")" > "$(basename "$out").sha256"); else (cd "$outdir" && shasum -a 256 "$(basename "$out")" > "$(basename "$out").sha256"); fi
echo "Encrypted backup created: $out"
echo "Restore has NOT been verified. Keep passphrase separately and run verify_restore.sh."
