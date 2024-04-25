# Generate certificate for nginx
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
