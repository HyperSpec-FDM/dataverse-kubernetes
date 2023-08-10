#!/bin/bash

# Set the paths
source_path="/opt/docroot/logos/"
target_path="/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/"

## Wait until Dataverse is ready
until curl -sS -f "http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}/robots.txt" -m 2 2>&1 > /dev/null; do
    echo "Waiting for Dataverse to become ready..."
    sleep 15
done

# Find the latest file in the source directory
latest_file=$(ls -t "$source_path" | head -n 1)

# Check if any file was found
if [ -n "$latest_file" ]; then
    # Copy the file to the target directory
    cp "$source_path$latest_file" "$target_path"

    # Perform the curl operation
    curl -X PUT -d "$latest_file" http://localhost:8080/api/admin/settings/:LogoCustomizationFile

    echo "Latest file '$latest_file' copied and curl operation performed."
else
    echo "No files found in source directory."
fi