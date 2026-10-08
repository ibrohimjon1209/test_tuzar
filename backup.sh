#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${DB_PATH:-/data/bot.db}"
BACKUP_DIR="${BACKUP_DIR:-/data/backups}"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 CLI topilmadi. Ubuntu serverda: sudo apt-get install sqlite3" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/bot-$STAMP.db"

if [ ! -f "$DB_PATH" ]; then
  echo "DB fayli topilmadi: $DB_PATH" >&2
  exit 1
fi

sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Keep the newest 7 backups only.
ls -1t "$BACKUP_DIR"/bot-*.db 2>/dev/null | tail -n +8 | xargs -r rm -f

echo "Backup created: $BACKUP_FILE"
