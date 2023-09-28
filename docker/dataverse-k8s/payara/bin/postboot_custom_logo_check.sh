#!/bin/bash

# Set the paths
source_path="/opt/docroot/logos/"
target_path="/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/"

# Check if the source directory exists
if [ -d "$source_path" ]; then
    # Find the latest image file in the source directory
    latest_image_file=$(find "$source_path" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.svg" \) -exec stat -c "%Y %n" {} \; | sort -nr | head -n 1 | awk '{print $2}')

    # Check if any image file was found
    if [ -n "$latest_image_file" ]; then
        # Copy the image file to the target directory
        cp "$latest_image_file" "$target_path"

        # Perform the curl operation
        curl -X PUT -d "$latest_image_file" http://localhost:8080/api/admin/settings/LogoCustomizationFile

        echo "Latest image file '$latest_image_file' copied and curl operation performed."
    else
        echo "No image files found in directory $source_path."
    fi
else
    echo "Directory '$source_path' not found."
fi