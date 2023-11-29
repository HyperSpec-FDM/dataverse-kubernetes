#!/bin/bash

# Set the directory and script
directory="/opt/docroot/metadata"
tsv_files="/opt/docroot/metadata/*.tsv"
properties_files="/opt/docroot/metadata/*.properties"
destination_tsv="/opt/payara/dvinstall/data/metadatablocks/"
destination_properties="/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/WEB-INF/classes/propertyFiles/"

# Run add metadata script if the directory with the persistent file exists
# Check if the directory exists
if [ -d "$directory" ]; then
    # Check if the directory is not empty
    if [ "$(ls -A "$directory")" ]; then

        # Process .properties files
        for properties_file in $properties_files; do
            if [ -f "$properties_file" ]; then
                cp "$properties_file" "$destination_properties"
                echo "Copying $properties_file to $destination_properties"
            fi
        done

        # Process .tsv files
        for tsv_file in $tsv_files; do
            if [ -f "$tsv_file" ]; then
                cp "$tsv_file" "destination_tsv"
                curl http://localhost:8080/api/admin/datasetfield/load -H "Content-type: text/tab-separated-values" -X POST --upload-file "$tsv_file"
                echo "Uploaded: $tsv_file"
            fi
        done

        # Update solr schema
        curl "http://localhost:8080/api/admin/index/solr/schema" | bash ./dvinstall/update-fields.sh /opt/payara/dvinstall/schema.xml

        # Find the Solr pod dynamically based on a label
        solr_pod_name=$(kubectl get pods -n "dv-test" -l app.kubernetes.io/name=solr -o jsonpath='{.items[0].metadata.name}')

        # Copy schema.xml from the local directory to the Solr pod's configuration directory
        kubectl cp /opt/payara/dvinstall/schema.xml "dv-test/$solr_pod_name:/opt/solr-9.3.0/server/solr/collection1/conf/schema.xml" -c solr

        # Copy schema.xml from the local directory to the Solr pod's data directory (if needed)
        kubectl cp /opt/payara/dvinstall/schema.xml "dv-test/$solr_pod_name:/var/solr/data/collection1/conf/schema.xml" -c solr

         # Reload solr collection to make
        curl "http://${SOLR_SERVICE_HOST}:${SOLR_SERVICE_PORT}/solr/admin/cores?action=RELOAD&core=collection1"

    else
        echo "Directory $directory is empty."
    fi
else
    echo "Directory $directory not found."
fi
