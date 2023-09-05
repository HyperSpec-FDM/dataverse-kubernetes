#!/bin/bash

# Set the directory and script
directory="/opt/docroot/languages"
file="/opt/docroot/languages/languages"
script_path="/opt/payara/scripts/addLanguages.sh"

# Run add language script if the directory with the persistent file exists
# Check if the directory exists
if [ -d "$directory" ]; then
    # Check if the directory is not empty
    if [ "$(ls -A "$directory")" ]; then
      # add languages
      if [ -f "$file" ]; then
        arguments=$(cat "$file" | tr -d '[],')
        "$script_path" $arguments
      fi
    else
        echo "Directory $directory is empty."
    fi
else
    echo "Directory $directory not found."
fi