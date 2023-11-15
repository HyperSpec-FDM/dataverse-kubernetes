#!/bin/bash
# Wait for solr to be ready and create collection
echo "Waiting for solr to become ready..."
wait-for-solr.sh
echo "Solr is ready. Starting creation of collection."
solr create_core -c collection1 -d server/solr/collection1/conf

#echo "Updating fields"
#TARGET="/opt/solr-9.3.0/server/solr/collection1/conf/schema.xml"
#SOURCE="/opt/solr-9.3.0/server/solr/collection1/conf/schema.xml"
#${SCHEMA_SCRIPT_DIR}/update-fields.sh -p "$TARGET" "$SOURCE"
