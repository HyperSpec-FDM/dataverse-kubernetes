#!/bin/bash

# Set the paths
source_path="/opt/docroot/logos/"
target_path="/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/resources/images/"


# Check if the source directory exists
if [ -d "$source_path" ]; then
    # Find the latest image file in the source directory
    latest_image_file=$(find "$source_path" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.svg" \) -exec identify -quiet {} \; | sort -k 6 -r | head -n 1)

    # Check if any image file was found
    if [ -n "$latest_image_file" ]; then
        # Extract the filename from the full output of the 'identify' command
        latest_image_file=$(echo "$latest_image_file" | awk '{print $1}')

        # Extract the filename from the full path
        filename=$(basename "$latest_image_file")

        # Copy the image file to the target directory
        cp "$latest_image_file" "$target_path$filename"

        # Perform the curl operation
        curl -s -X PUT -F "file=@/resources/images/$filename" http://localhost:8080/api/admin/settings/LogoCustomizationFile > /dev/null 2>&1

        echo "Latest image file '$filename' copied and curl operation performed."
    else
        echo "No image files found in directory $source_path."
    fi
else
    echo "Directory '$source_path' not found."
fi