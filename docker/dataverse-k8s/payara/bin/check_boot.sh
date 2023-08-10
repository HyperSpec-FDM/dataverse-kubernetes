#!/bin/bash

## Wait until Dataverse is ready
until curl -sS -f "http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}/robots.txt" -m 2 2>&1 > /dev/null; do
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