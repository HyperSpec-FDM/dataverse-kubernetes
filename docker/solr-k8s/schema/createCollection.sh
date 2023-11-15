#!/bin/bash

# Start Solr in the background
solr -f -a "-Dlog4j.configurationFile=/opt/solr-9.3.0/server/resources/log4j2.xml" &

# Function to check if Solr is ready
function check_solr_ready() {
    until solr status; do
        echo "Waiting for Solr to be ready..."
        sleep 3
    done
}

# Main script
check_solr_ready
echo "Solr is ready! Creating collection1..."
solr create_core -c collection1 -d server/solr/collection1/conf

# Keep the script running to prevent the container from exiting
tail -f /dev/null