FROM centos/httpd:latest

# Install required packages
COPY docker/apache-k8s/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo
RUN yum update -y && yum install mod_ssl -y

# Add startup script
COPY docker/apache-k8s/run-httpd.sh /usr/local/bin/run-httpd.sh

# Add your Apache configurations here (e.g., httpd.conf)
COPY docker/apache-k8s/conf/dataverse.conf /etc/httpd/conf.d/dataverse.conf
COPY docker/apache-k8s/conf/ssl.conf /etc/httpd/conf.d/ssl.conf

# Make the script executable
RUN chmod +x /usr/local/bin/run-httpd.sh

EXPOSE 80
EXPOSE 443

# Start Apache with your entry point script
ENTRYPOINT ["/usr/local/bin/run-httpd.sh"]
