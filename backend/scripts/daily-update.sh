#!/bin/bash
set -euo pipefail

APP_NAME=$(basename $(pwd))
echo "========== $(date) =========="
echo ">>> Backing up database for $APP_NAME"

BAK_FILE=db.sqlite3.bak-$(date +%Y%m%d)
if [ -e "${BAK_FILE}" ]; then
	echo ">>> It has been updated already today"
	exit 0
fi
cp -av db.sqlite3 ${BAK_FILE}

# Keep only the 7 most recent backups (filename dates sort lexicographically)
find . -maxdepth 1 -name 'db.sqlite3.bak-*' -printf '%f\n' | sort | head -n -7 | xargs -r rm -fv

echo ">>> Database backup done for $APP_NAME"
