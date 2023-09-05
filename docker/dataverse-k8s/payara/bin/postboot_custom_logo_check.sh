#!/bin/bash

# Set the paths
source_path="/opt/docroot/logos/"
target_path="/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/"

# Check if the source directory exists
if [ -d "$source_path" ]; then
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
        echo "Directory $source_path is empty.."
    fi
else
    echo "Directory '$source_path' not found."
fi



