FROM centos/httpd:latest

# Create a Shibboleth repository configuration file
COPY docker/shibboleth-k8s/shibboleth.repo /etc/yum.repos.d/shibboleth.repo

# Install required packages
RUN yum -y install httpd mod_ssl shibboleth vim

# Add startup script
COPY docker/shibboleth/run-httpd.sh /usr/local/bin/run-httpd.sh

# Add your Shibboleth and Apache configurations here (e.g., shibboleth2.xml, httpd.conf)
COPY docker/shibboleth-k8s/conf/dataverse.conf /etc/httpd/conf.d/dataverse.conf
COPY docker/shibboleth-k8s/conf/ssl.conf /etc/httpd/conf.d/ssl.conf
COPY docker/shibboleth-k8s/conf/shibboleth2.xml /etc/shibboleth/shibboleth2.xml
COPY docker/shibboleth-k8s/conf/dataverse-idp/dataverse-idp-metadata.xml /etc/shibboleth/dataverse-idp-metadata.xml
COPY docker/shibboleth-k8s/conf/dataverse-idp/attribute-map.xml /etc/shibboleth/attribute-map.xml

# Make the script executable
RUN chmod +x /usr/local/bin/run-httpd.sh

EXPOSE 80
EXPOSE 443

# Start Apache with your entry point script
ENTRYPOINT ["/usr/local/bin/run-httpd.sh"]
