# Copyright 2019 Forschungszentrum Jülich GmbH
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

FROM payara/server-full:5.2022.3-jdk11
LABEL maintainer="FDM FZJ <forschungsdaten@fz-juelich.de>"

EXPOSE 4848 9009 8080 8181

ARG VERSION=5.14
ARG DOMAIN=domain1

ENV DATA_DIR=/data\
    DOCROOT_DIR=/opt/docroot\
    METADATA_DIR=/metadata\
    SECRETS_DIR=/secrets\
    DUMPS_DIR=/dumps\
    DOMAIN_DIR=${PAYARA_DIR}/glassfish/domains/${DOMAIN_NAME}\
    DATAVERSE_VERSION=${VERSION}\
    DATAVERSE_PKG=https://github.com/IQSS/dataverse/releases/download/v${VERSION}/dvinstall.zip\
    PGDRIVER_PKG=https://jdbc.postgresql.org/download/postgresql-42.2.12.jar\
#    PGDRIVER_PKG=https://jdbc.postgresql.org/download/postgresql-42.2.23.jar\
    # Make heap dumps on OOM appear in DUMPS_DIR
    JVM_ARGS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=\${ENV=DUMPS_DIR}"

# Create basic pathes
USER root
RUN mkdir -p ${HOME_DIR} ${SCRIPT_DIR} ${SECRETS_DIR} && \
    mkdir -p ${DATA_DIR} ${METADATA_DIR} ${DOCROOT_DIR} ${DUMPS_DIR} && \
    mkdir -p ${DOMAIN_DIR}&& \
    chown -R payara: ${DATA_DIR} ${METADATA_DIR} ${DOCROOT_DIR} ${SECRETS_DIR} ${DUMPS_DIR}

## Install prerequisites
#RUN apt-get -qq update && \
#    apt-get -qqy install postgresql-client jq imagemagick curl wget unzip
# Install prerequisites
#RUN sed -rz -i 's/http/https/g' /etc/apt/sources.list
RUN apt-get -qq update && \
    apt-get -qqy install postgresql-client jq imagemagick curl wget unzip vim python3.8 python3-distutils python3-apt  python3-psycopg2 ed bc original-awk python3-pandas lsb-release patch cron git zip
RUN wget --no-verbose  https://bootstrap.pypa.io/get-pip.py -O -|/usr/bin/python3.8

# Install esh template engine from Github
RUN wget --no-verbose -O esh https://raw.githubusercontent.com/jirutka/esh/v0.3.0/esh && \
    echo 'fe030e23fc1383780d08128eecf322257cec743b esh' | sha1sum -c - && \
    chmod +x esh && mv esh /usr/local/bin

# change permission of /opt to enable logo upload for dataverse collection
RUN chown -R payara:payara /opt
# change permission of /opt to enable logo upload for dataverse collection

# Install PostgreSQL JDBC driver in AppServer
# TODO: remove this once upstream includes the Postgres Client lib in the WAR.
USER payara
#RUN wget --no-verbose -O postgresql.jar ${PGDRIVER_PKG} && \
#    mv postgresql.jar ${PAYARA_DIR}/glassfish/lib

# Make docroot of Payara reside in higher level directory for easier targeting
# Due to IQSS/dataverse-kubernetes#177: create the generated pathes so they are
# writeable by us. TBR with #178.
RUN rm -rf ${DOMAIN_DIR}/docroot && \
    ln -s ${DOCROOT_DIR} ${DOMAIN_DIR}/docroot && \
    mkdir -p ${DOMAIN_DIR}/generated/jsp/dataverse

# Retrieve the Dataverse install package, extract and remove ZIP,
#    symlink WAR file and remove Harvard custom metadatablocks
RUN cd ${HOME_DIR} && \
    wget --no-verbose -O dvinstall.zip ${DATAVERSE_PKG} && \
    unzip -qq dvinstall.zip -d ./ && \
    rm dvinstall.zip
    #&& \
#    ln -s ${HOME_DIR}/dvinstall/dataverse.war ${DEPLOY_DIR}/dataverse.war && \
#    find . -iname "custom*.tsv" -delete

# pg diver in dir like in version 4.20
RUN mkdir /opt/payara/dvinstall/pgdriver
RUN wget --no-verbose -O postgresql.jar ${PGDRIVER_PKG} && \
    mv postgresql.jar /opt/payara/dvinstall/pgdriver

# Copy across docker scripts
COPY --chown=payara:payara docker/dataverse-k8s/bin/* docker/dataverse-k8s/payara/bin/*.sh ${SCRIPT_DIR}/
RUN chmod +x ${SCRIPT_DIR}/*

# Copy config
COPY --chown=payara:payara docker/dataverse-k8s/bin/*.config ${SCRIPT_DIR}/
COPY --chown=payara:payara docker/dataverse-k8s/payara/*.config /opt/payara/dvinstall/default.config

# Copy reference_data
COPY --chown=payara:payara docker/dataverse-k8s/payara/reference_data.sql /opt/payara/dvinstall/reference_data.sql

# Copy logging.properties
COPY --chown=payara:payara docker/dataverse-k8s/payara/logging.properties ${PAYARA_DIR}/glassfish/domains/${DOMAIN_NAME}/config/logging.properties
