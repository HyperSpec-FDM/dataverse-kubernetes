FROM quay.io/keycloak/keycloak

# copy realm and client scope
COPY /docker/keycloak-idp-k8s/conf/realm.json /opt/keycloak/data/import/realm.json
COPY /docker/keycloak-idp-k8s/conf/client.json  /opt/keycloak/data/client.json

# Copy the scripts into the container
COPY /docker/keycloak-idp-k8s/bin/configure_keycloak.sh /opt/keycloak/configure_keycloak.sh
COPY /docker/keycloak-idp-k8s/bin/start_up.sh /opt/keycloak/start_up.sh

# Set the working directory
WORKDIR /opt/keycloak

# Expose the ports
EXPOSE 8443

# Set required envs to prevent indefinite loading of admin console
ENV KC_PROXY=edge

#ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
#CMD ["start-dev", "--import-realm"]

ENTRYPOINT ["/opt/keycloak/start_up.sh"]
