#!/bin/bash

# Check if both arguments are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 env value"
  exit 1
fi

# Set environment variable
export "$1='$2'"

# Display the updated environment variable
echo "Environment variable $1 set to $2"
