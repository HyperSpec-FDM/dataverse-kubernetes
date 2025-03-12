#!/bin/bash

/opt/keycloak/configure_keycloak.sh &
/opt/keycloak/bin/kc.sh start --import-realm
