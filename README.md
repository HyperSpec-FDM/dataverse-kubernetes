# Deploying, Running and Using Dataverse on Kubernetes

![Dataverse badge](https://img.shields.io/badge/Dataverse-v6.2-important.svg) ![Validation badge](https://jenkins.dataverse.org/job/dataverse-k8s/job/Kubeval%20Linting/job/release/badge/icon?subject=kubeval&status=valid&color=purple) ![DockerHub dataverse-k8s badge](https://img.shields.io/static/v1.svg?label=image&message=dataverse-k8s&logo=docker) ![DockerHub solr-k8s badge](https://img.shields.io/static/v1.svg?label=image&message=solr-k8s&logo=docker) ![License badge](https://img.shields.io/github/license/IQSS/dataverse-kubernetes) [![Docs badge](https://readthedocs.org/projects/dataverse-k8s/badge/?version=latest)](https://dataverse-k8s.rtfd.io/en/latest) [![IRC badge](https://img.shields.io/badge/IRC%20chat-%23dataverse-blue)](https://kiwiirc.com/client/irc.freenode.net/?nick=dataverse_k8s_?#dataverse)

This community-supported project aims at offering a new way to deploy, run and maintain a Dataverse installation for any purpose on any kind of Kubernetes-based cloud infrastructure.

You can use this on your laptop, in your on-prem datacentre or public cloud. With the power of [Kubernetes](http://kubernetes.io), many scenarios are possible.

- Documentation: [https://dataverse-k8s.rtfd.io](https://dataverse-k8s.rtfd.io)
- Support and new ideas: [https://github.com/IQSS/dataverse-kubernetes/issues](https://github.com/IQSS/dataverse-kubernetes/issues)

If you would like to contribute, you are most welcome.

This project follows the same branching strategy as the upstream Dataverse project, using a `release` branch for stable releases plus a `develop` branch. In this branch unexpected or breaking changes may happen.

## Prerequisites

1. **Running Kubernetes Cluster**
2. **Setup Networking for Kubernetes**
3. **Private Docker Registry**

## Usage

1. **Configure variables** for image building in [buildImages.py](Scripts/buildImages.py)
2. **Build images** for Dataverse, Solr and Shibboleth\
and push them to your private registry.

    Run [buildImages.py](Scripts/buildImages.py)
    ````
    python3 Scripts/buildImages.py
    ````
3. Deploy Dataverse to your Kubernetes Cluster

    Run [deploy.py](Scripts/deploy.py)
    ````
    python3 Scripts/deploy.py.py
    ````
## Configuration
### OpenID Connect
#### Prerequisites
1. **Dataverse running in cluster running using a virtual network**
2. **nginx setup as reverse proxy for Dataverse**

#### Generate certificate for nginx
1. Open the `san.cnf` file for editing:
```
sudo vim san.cnf
```
2. Add the following configuration:

```
[req]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
countryName = DE
stateOrProvinceName = BW
localityName = N/A
organizationName = Self-signed certificate
commonName = 120.0.0.1: Self-signed certificate

[req_ext]
subjectAltName = @alt_names

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = IP
IP.2 = vlan IP
```

3. Generate the certificate and key using OpenSSL:
```
sudo openssl req -x509 -nodes -days 730 -newkey rsa:2048 -keyout key.pem -out cert.pem -config san.cnf
```

# Enable certificate
1. Add the certificate and key to the nginx sites_enabled section for Keycloak.
2. Check nginx configuration:
```
sudo nginx -t
```
3. Reload nginx:
```
sudo systemctl reload nginx
```

# Enable keycloak in dataver
1. Add to Dataverse Dockerfile:
```
COPY docker/dataverse-k8s/payara/oidc-provider.crt /tmp/my-oidc-provider.crt
RUN keytool -importcert -alias oidc-provider -file /tmp/my-oidc-provider.crt -keystore /opt/payara/appserver/glassfish/domains/domain1/config/cacerts.p12 -storepass changeit -noprompt
```
Imports the generated, self-signed certificate into Dataveres truststore.

2. Open Bash to Dataverse Pod:
```
kubectl exec -it POD-NAME -c datavers -- bash
```
3. Inside the Dataverse pod, create a file named my-oidc-provider.json with the following content:
```
{
    "id":"<a unique id>",
    "factoryAlias":"oidc",
    "title":"<a title - shown in UI>",
    "subtitle":"<a subtitle - currently unused in UI>",
    "factoryData":"type: oidc | issuer: <issuer url> | clientId: <client id> | clientSecret: <client secret> | pkceEnabled: <true/false> | pkceMethod: <PLAIN/S256/...>",
    "enabled":true
}
```
4. Upload the JSON file to Dataverse using curl:
```
{
curl -X POST -H 'Content-type: application/json' --upload-file my-oidc-provider.json http://localhost:8080/api/admin/authenticationProviders
}

