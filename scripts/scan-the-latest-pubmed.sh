#!/bin/bash

PUBMED_XML_GZ=$(find pubmed/updatefiles/ -type f -name '*.xml.gz' | sort | tail -n1)
echo "Latest PubMed XML file: $PUBMED_XML_GZ"

SOURCE=$(basename $PUBMED_XML_GZ .xml.gz)
SOURCE=${SOURCE#pubmed24n}
echo "Got source: $SOURCE"

mkdir -pv log/pubmed
./.venv/bin/python scripts/import-pubmed.py pubmed $SOURCE -r -m default >>log/pubmed/$SOURCE.log 2>&1
#./.venv/bin/python scripts/import-pubmed.py pubmed $SOURCE -r -m update-index >>log/pubmed/$SOURCE-update-index.log 2>&1
