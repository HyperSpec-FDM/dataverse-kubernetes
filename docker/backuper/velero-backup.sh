#!/bin/bash

set -e

# Number of backups to keep from the environment variable, default to 4 if not set
BACKUP_COUNT_TO_KEEP=${BACKUP_COUNT_TO_KEEP:-4}

# Generate a timestamped backup name and start backup
BACKUP_NAME="my-backup-$(date +\%Y\%m\%d\%H\%M)"
echo "Starting Velero backup: $BACKUP_NAME"
velero backup create $BACKUP_NAME --include-namespaces dv-test --default-volumes-to-fs-backup

# Wait for backup to complete
echo "Waiting for backup to complete..."
while true; do
  STATUS=$(velero backup get $BACKUP_NAME --output=json | jq -r '.status.phase')
  echo "Current status: $STATUS"

  if [ "$STATUS" = "Completed" ]; then
    echo "Backup $BACKUP_NAME completed successfully."
    break
  elif [ "$STATUS" = "Failed" ] || [ "$STATUS" = "PartiallyFailed" ]; then
    echo "Backup $BACKUP_NAME failed or partially failed!"
    exit 1
  fi

  sleep 30  # Wait before checking again
done

# Cleanup: Keep only the latest 4 backups
echo "Checking for old backups to delete..."
#BACKUPS=$(velero get backups --output=json | jq -r '.items | sort_by(.metadata.creationTimestamp) | .[].metadata.name')
BACKUPS=$(velero get backups --output=json | jq -r 'if .items then .items | map(.metadata) else [.] | map(.metadata) end | sort_by(.creationTimestamp) | .[].name')

# Count the total number of backups
BACKUP_COUNT=$(echo "$BACKUPS" | wc -l)

if [ "$BACKUP_COUNT" -gt "$BACKUP_COUNT_TO_KEEP" ]; then
  DELETE_COUNT=$((BACKUP_COUNT - BACKUP_COUNT_TO_KEEP))
  echo "Deleting $DELETE_COUNT old backups..."
  echo "$BACKUPS" | head -n $DELETE_COUNT | xargs -I {} velero backup delete {} --confirm
else
  echo "No backups for deletion. Current count: $BACKUP_COUNT, keeping $BACKUP_COUNT_TO_KEEP backups."
fi

echo "Finished backup. Exiting now."