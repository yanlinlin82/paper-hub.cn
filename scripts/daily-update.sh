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
find -name 'db.sqlite3.bak-*' -mtime +7 -exec rm -fv "{}" \;

echo ">>> Database backup done for $APP_NAME"
