FROM ubuntu:22.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl jq bash \
    && rm -rf /var/lib/apt/lists/*

# Install Velero
RUN curl -L https://github.com/vmware-tanzu/velero/releases/download/v1.15.2/velero-v1.15.2-linux-amd64.tar.gz \
    | tar -xz && mv velero-v1.15.2-linux-amd64/velero /usr/local/bin/velero && rm -rf velero-v1.15.2-linux-amd64

# Copy backup script
COPY docker/backuper/velero-backup.sh /usr/local/bin/velero-backup.sh
RUN chmod +x /usr/local/bin/velero-backup.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/velero-backup.sh"]
