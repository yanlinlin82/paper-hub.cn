#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_ROOT="${1:-${SRC_ROOT}/../paper-tracker}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
EXPORT_DIR="${TARGET_ROOT}/data-migration/${TIMESTAMP}"

if [[ ! -d "${TARGET_ROOT}" ]]; then
  echo "Target project directory does not exist: ${TARGET_ROOT}" >&2
  exit 1
fi

mkdir -p "${EXPORT_DIR}"

MODELS=(
  auth.user
  core.userprofile
  core.label
  core.paper
  core.paperreference
  core.papertranslation
  core.paperchat
  core.papertracking
  core.recommendation
)

cd "${SRC_ROOT}"

echo "[1/3] Exporting data to ${EXPORT_DIR}/paper_tracker_data.json"
uv run python manage.py dumpdata --indent 2 --output "${EXPORT_DIR}/paper_tracker_data.json" "${MODELS[@]}"

echo "[2/3] Writing record counts to ${EXPORT_DIR}/counts.json"
uv run python - <<'PY' > "${EXPORT_DIR}/counts.json"
import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Label, Paper, PaperReference, PaperTranslation, PaperChat, PaperTracking, Recommendation

counts = {
  'auth.user': User.objects.count(),
  'core.userprofile': UserProfile.objects.count(),
  'core.label': Label.objects.count(),
  'core.paper': Paper.objects.count(),
  'core.paperreference': PaperReference.objects.count(),
  'core.papertranslation': PaperTranslation.objects.count(),
  'core.paperchat': PaperChat.objects.count(),
  'core.papertracking': PaperTracking.objects.count(),
  'core.recommendation': Recommendation.objects.count(),
}
print(json.dumps(counts, ensure_ascii=False, indent=2))
PY

echo "[3/3] Writing import guide to ${EXPORT_DIR}/README.md"
cat > "${EXPORT_DIR}/README.md" <<'EOF'
# paper-tracker data package

This package contains data exported from paper-hub.cn for features moved to paper-tracker.

## Files
- `paper_tracker_data.json`: Django fixture exported by `dumpdata`.
- `counts.json`: row counts at export time.

## Included models
- `auth.user`
- `core.userprofile`
- `core.label`
- `core.paper`
- `core.paperreference`
- `core.papertranslation`
- `core.paperchat`
- `core.papertracking`
- `core.recommendation`

## Import command (run in paper-tracker)

```sh
uv run python manage.py loaddata data-migration/<timestamp>/paper_tracker_data.json
```

If your target app labels/model names differ, load this file with a custom importer or transform model labels before import.
EOF

sha256sum "${EXPORT_DIR}/paper_tracker_data.json" > "${EXPORT_DIR}/paper_tracker_data.sha256"

printf "\nExport completed:\n- %s\n" "${EXPORT_DIR}"
