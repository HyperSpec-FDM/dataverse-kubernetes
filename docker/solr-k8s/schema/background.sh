#!/bin/bash
# Wait for solr to be ready and create collection
echo "Waiting for solr to become ready..."
wait-for-solr.sh
echo "Solr is ready. Starting creation of collection."
solr create_core -c collection1 -d server/solr/collection1/conf