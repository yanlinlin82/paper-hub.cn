#!/bin/bash
#
# Push locally generated member reports to the production server.
#
# The report is generated on the host from a local copy of the production
# database (see fetch-online-db.sh), but backend/reports/ is gitignored, so a
# code deploy never carries it. Run this after generate_member_report.
#
# Usage:
#   ./scripts/push-reports.sh [DEST]
#
# DEST defaults to the reports directory on the production server.

set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../.."; pwd)
REPORTS_DIR="$PROJECT_DIR/backend/reports"
DEST="${1:-yanlinlin.cn:/var/www/paper-hub.cn/backend/reports/}"

# Guard: `--delete` against an empty local directory would wipe the server copy.
if ! compgen -G "$REPORTS_DIR/*.json" > /dev/null; then
	echo "No report in $REPORTS_DIR; run generate_member_report first." >&2
	exit 1
fi

# --delete drops member files whose reviews no longer exist, so the server never
# keeps serving a profile that was removed from the database.
rsync -avP --delete "$REPORTS_DIR/" "$DEST"
