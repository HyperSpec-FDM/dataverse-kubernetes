#!/bin/bash

# Set the directory and script
directory="/opt/docroot/mail"
test_file="$directory/add_mail.txt"

# Run add metadata script if the directory with the persistent file exists
# Check if the directory exists
if [ -d "$directory" ]; then
    # Check if the directory is not empty
    if [ "$(ls -A "$directory")" ]; then

        # Check if test.txt exists and is a file
        if [ -f "$test_file" ]; then
            # Read and execute the content of test.txt
            asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile  delete-javamail-resource mail/notifyMailSession
            source "$test_file"
            echo "Executed contents of $test_file"
        else
            echo "File $test_file not found."
        fi

    else
        echo "Directory $directory is empty."
    fi
else
    echo "Directory $directory not found."
fi


