#!/bin/bash

# Fail on any error (but not errexit, as we want to be gracefull!)
set -uo pipefail

DATAVERSE_SERVICE_HOST=${DATAVERSE_SERVICE_HOST:-"dataverse"}
DATAVERSE_SERVICE_PORT_HTTP=${DATAVERSE_SERVICE_PORT_HTTP:-"8080"}
DATAVERSE_URL=${DATAVERSE_URL:-"http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}"}
SOLR_URL="http://localhost:8983"
TARGET="/opt/solr-8.11.1/server/solr/collection1/conf/schema.xml"
#SOURCE=""
SOURCE="/opt/solr-8.11.1/server/solr/collection1/conf/schema.xml"

# Check API key secret is available
if [ ! -s "/scripts/schema/api/key" ]; then
  echo "No API key present. Failing."
  exit 126
fi
UNBLOCK_KEY=`cat /scripts/schema/api/key`

## Dataverse readiness check
#until curl -sS -f "http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}/robots.txt" -m 2 2>&1 > /dev/null; do
#  echo "Waiting for Dataverse"
#  sleep 15
#done

## Retrieve the schema from Dataverse
#SOURCE=$(curl "${DATAVERSE_URL}/api/admin/index/solr/schema")

## Check if <field> or <copyField> definitions exist in the retrieved schema
#if echo "$SOURCE" | grep -q -e "<field\|<copyField"; then
#  echo "The <field> or <copyField> exists in the retrieved schema"
#else
#  echo "No <field> or <copyField> in input"
#  exit 1
#fi

# Now that Solr is ready, execute the solr create_core command
solr create_core -c collection1 -d server/solr/collection1/conf

${SCHEMA_SCRIPT_DIR}/update-fields.sh -p "$TARGET" "$SOURCE"
echo "It was executed"
#  -t "$TARGET" \
#  -s "$SOLR_URL" \
#  -u "$UNBLOCK_KEY" \
#  -d "$DATAVERSE_URL" \
#  || echo "Failing gracefully to allow startup."
