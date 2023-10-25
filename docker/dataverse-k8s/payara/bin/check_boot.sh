#!/bin/bash

# Wait until Dataverse is ready
until curl -sS -f "http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}" -m 2 2>&1 > /dev/null; do
    echo "Waiting for Dataverse to become ready..."
    sleep 15
done

# Run postboot scripts
for f in ${SCRIPT_DIR}/postboot_*; do
    case "$f" in
        *.sh)
            echo "[Postboot] running $f"
            . "$f"
            ;;
        *)
            echo "[Postboot] ignoring $f"
            ;;
    esac
    echo
done


## Wait until Dataverse is fully setup
#echo "Starting with checking for set DoiProvider"
#until response=$(curl -sS -f "http://localhost:${DATAVERSE_SERVICE_PORT_HTTP}/api/admin/settings/:DoiProvider" -m 2 2>&1); do
#    echo "Waiting for Dataverse setup to finish..."
#    echo "Curl Output: $response"
#    sleep 15
#done
#
## Run config-jon
#echo "Running bootstrap-job and config-job"
#${SCRIPT_DIR}/bootstrap-job.sh