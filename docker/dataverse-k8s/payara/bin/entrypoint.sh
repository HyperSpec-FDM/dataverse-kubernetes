#!/bin/bash

# "--verbose" starts the domain in foreground using Glassfish 4.1
# TODO: It would be better to follow the Payara approach and execute the JVM
#       directly to avoid a doubled JVM, but this seems impossible with
#       a "vanilla" Glassfish 4.1 (the appserver simply doesn't start).
#       Maybe using a Payara 4.x appserver can help with this.
#exec ${GLASSFISH_DIR}/bin/asadmin start-domain --verbose

# TEST with fixed line endings
# Fix line endings in default.config
sed -i 's/\r$//' /opt/payara/scripts/default.config

# Function to check if directory is empty
is_directory_empty() {
    local dir="$1"
    if [ -d "$dir" ] && [ "$(ls -A "$dir")" == "" ]; then
        return 0  # Directory is empty
    else
        return 1  # Directory is not empty
    fi
}

# Run init scripts (credits go to MySQL Docker entrypoint script)
for f in ${SCRIPT_DIR}/init_* ${SCRIPT_DIR}/init.d/*; do
    case "$f" in
        *.sh)
            echo "[Entrypoint] running $f"
            . "$f"
            ;;
        *)
            echo "[Entrypoint] ignoring $f"
            ;;
    esac
    echo
done


# Check if /opt/doroot/ is empty (indicating initial boot)
if is_directory_empty "/opt/docroot/"; then
    echo "[Init] Detected initial boot"
    exec ${SCRIPT_DIR}/startInForeground.sh $PAYARA_ARGS

else
    echo "[Init] Detected content in /opt/docroot/"
    # Runs first script in background for postboot tasks
    ${SCRIPT_DIR}/check_boot.sh &
    exec ${SCRIPT_DIR}/startInForeground.sh $PAYARA_ARGS

fi

#if [ "${GIT_CVM_TEMPLATES}" ]; then
#    #echo "Clone dataverse templates from ${GIT_CVM_TEMPLATES}" >> /tmp/status.log;
#    #git clone ${GIT_CVM_TEMPLATES} /tmp/cvm-templates;
#    #cd /tmp/cvm-templates; git fetch; git pull origin master;
#    cp -R /tmp/cvm-templates/templates/dataverse/* /opt/payara/appserver/glassfish/domains/production/applications/dataverse/
#fi