#!/bin/bash
set -euo pipefail

APP_NAME=$(basename $(pwd))
echo "========== $(date) =========="
echo ">>> Updating for $APP_NAME"

BAK_FILE=db.sqlite3.bak-$(date +%Y%m%d)
if [ -e "${BAK_FILE}" ]; then
	echo ">>> It has been updated already today"
	exit 0
fi
cp -av db.sqlite3 ${BAK_FILE}
find -name 'db.sqlite3.bak-*' -mtime +7 -exec rm -fv "{}" \;

PUBMED_XML_GZ=$(find pubmed/updatefiles/ -type f -name '*.xml.gz' | sort | tail -n1)
if [ -z "$PUBMED_XML_GZ" ]; then
	echo ">>> ERROR: No PubMed XML file found under pubmed/updatefiles/"
	exit 1
fi
echo ">>> Latest PubMed XML file: $PUBMED_XML_GZ"

SOURCE=$(basename "$PUBMED_XML_GZ" .xml.gz)
if [ -z "$SOURCE" ]; then
	echo ">>> ERROR: Failed to derive source name from $PUBMED_XML_GZ"
	exit 1
fi
echo ">>> Got source: $SOURCE"

mkdir -pv log/pubmed
if ! ./.venv/bin/python scripts/import-pubmed.py pubmed "$SOURCE" -r -m default >>"log/pubmed/$SOURCE.log" 2>&1; then
	echo ">>> ERROR: import-pubmed default mode failed, see log/pubmed/$SOURCE.log"
	tail -n20 "log/pubmed/$SOURCE.log"
	exit 1
fi

if ! ./.venv/bin/python scripts/import-pubmed.py pubmed "$SOURCE" -r -m update-index >>"log/pubmed/$SOURCE-update-index.log" 2>&1; then
	echo ">>> ERROR: import-pubmed update-index mode failed, see log/pubmed/$SOURCE-update-index.log"
	tail -n20 "log/pubmed/$SOURCE-update-index.log"
	exit 1
fi

tail -n2 "log/pubmed/$SOURCE.log"
echo ">>> Updating for $APP_NAME done"
