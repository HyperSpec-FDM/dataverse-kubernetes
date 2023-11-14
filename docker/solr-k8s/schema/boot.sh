#!/bin/bash

# Define script to run in background
exec /scripts/schema/background.sh &

#Start solr in the foreground
solr -f -a "-Dlog4j.configurationFile=/opt/solr-9.3.0/server/resources/log4j2.xml"