#!/bin/bash

# Wait for Keycloak server to start
until timeout 10s bash -c 'cat < /dev/null > /dev/tcp/localhost/8080'; do
    printf '.'
    sleep 5
done

# Configure Keycloak credentials
/opt/keycloak/bin/kcadm.sh config credentials --server http://141.19.44.18:8180 --realm master --user admin --password admin

# Disable ssl
/opt/keycloak/bin/kcadm.sh update realms/master -s sslRequired=NONE
#/opt/keycloak/bin/kcadm.sh update realms/master -s sslRequired=external

# Import client scope
/opt/keycloak/bin/kcadm.sh create clients -r master -f /opt/keycloak/data/client.json