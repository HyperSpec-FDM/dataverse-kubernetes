#!/bin/bash

# Set the directory and script
directory="/opt/docroot/s3"
script_path="/opt/payara/scripts/newS3Storage.sh"

# create jvm options from every file in directory if present

# Check if the directory exists
if [ -d "$directory" ]; then
    # Check if the directory is not empty
    if [ "$(ls -A "$directory")" ]; then
      # create jvm options
        for file in "$directory"/*; do
            if [ -f "$file" ]; then
                arguments=$(cat "$file" | tr -d '[],')
                "$script_path" $arguments
            fi
        done
    else
        echo "Directory $directory is empty."
    fi
else
    echo "Directory $directory not found."
fi