from class_dataverse_curler import dataverse_curler
import json
from datetime import datetime
import os

local = False
# get enviroment variables
if local:
    url = "http://localhost:8080/"
    api_key = "b3752a5a-3a15-4dcc-9f7f-921c216dadcc"
    dataverse_id = "HyperSpec-FDM"
    deployment_name = "dataverse"
    namespace = "dv-test"
    container_name = "dataverse"
else:
    url = os.environ["url"]
    api_key = os.environ["api_key"]
    dataverse_id = os.environ["dataverse_id"]
    deployment_name = os.environ["deployment_name"]
    namespace = os.environ["namespace"]
    container_name = os.environ["container_name"]

# get current date
date = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
print(date)

# instantiate curler
curler = dataverse_curler(deployment_name, namespace, container_name, url, api_key)

# get content of dataverse
output = curler.curl_dataverse(dataverse_id)
data = json.loads(output["STDOUT"])["data"]

# read datasets and extract the ones to delete
datasets_to_delete = []
for item in data:
    if item["type"] == "dataset":
        persistent_id = item["protocol"] + ":" + item["authority"] + "/" + item["identifier"]
        meta = curler.curl_dataset(persistent_id)
        meta = json.loads(meta["STDOUT"])
        fields = meta["data"]["metadataBlocks"]["citation"]["fields"]
        for field in fields:
            if field["typeName"] == "dateOfDeletion":
                date_of_deletion = datetime.strptime(field["value"], "%Y-%m-%d")
                print(f"{persistent_id}: {date_of_deletion}")
                if date_of_deletion < date:
                    datasets_to_delete.append(persistent_id)

for item in datasets_to_delete:
    print(f"Deleting dataset with persistent identifiers: {item}")
    curler.delete_dataset(item)

if datasets_to_delete == []:
    print("No Datasets to delete")

