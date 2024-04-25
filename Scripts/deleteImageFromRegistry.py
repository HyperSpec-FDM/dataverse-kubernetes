import os
import subprocess
import requests


# name = "dataverse_deleter"

# define variables for registry
registry = "192.168.100.11:31000"
user = "tim"
password = "changeme"


# Get the list of tags
tags_response = requests.get(f"https://{registry}/v2/{name}/tags/list", verify=False, auth=(user, password))
tags_response.raise_for_status()
tags_json = tags_response.json()
latest_tag = tags_json['tags'][0]
print(tags_json)

# Get the digest of the manifest associated with the latest tag
manifest_headers = {
    "Accept": "application/vnd.docker.distribution.manifest.v2+json"
}
manifest_response = requests.head(f"https://{registry}/v2/{name}/manifests/{latest_tag}", headers=manifest_headers, verify=False, auth=(user, password))
manifest_response.raise_for_status()
digest = manifest_response.headers['Docker-Content-Digest']
print(digest)

# Delete the manifest using the digest
delete_response = requests.delete(f"https://{registry}/v2/{name}/manifests/{digest}", verify=False, auth=(user, password))
delete_response.raise_for_status()

print("Manifest deleted successfully.")
