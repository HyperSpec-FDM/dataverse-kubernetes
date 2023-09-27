import os
from kubernetes import client, config
import subprocess
from PIL import Image
from xml.etree import ElementTree as ET

def get_pod_name_by_deployment(deployment_name, namespace, container_name):
    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create an instance of the Kubernetes AppsV1 API client
    apps_v1 = client.AppsV1Api()

    # Get the deployment object
    deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)

    # Get the labels selector for the deployment's pod template
    labels = deployment.spec.selector.match_labels

    # Create an instance of the Kubernetes CoreV1 API client
    core_v1 = client.CoreV1Api()

    # List pods in the same namespace with matching labels
    pods = core_v1.list_namespaced_pod(namespace, label_selector=','.join(f"{k}={v}" for k, v in labels.items())).items

    # Return the name of the first pod (assuming there is only one)
    if pods:
        for pod in pods:
            print(f"Containers in pod '{pod.metadata.name}':")
            for container_status in pod.status.container_statuses:
                name = container_status.name
                container_id = container_status.container_id
                if name == container_name:
                    cid = container_id.replace("docker://", "")
        return pods[0].metadata.name, cid
    else:
        return None

# Usage
deployment_name = "dataverse"
namespace = "dv-test"  # Replace with the appropriate namespace
containername = "dataverse"
metadataFile = "testmeta.tsv"
apiBlocked = True

pod_name, containerID = get_pod_name_by_deployment(deployment_name, namespace, containername)
print(os.getcwd())
if pod_name:
    print(f"The pod name created by deployment '{deployment_name}' is '{pod_name}'.")

    metadataFile_path = "../metadata/" + metadataFile

    # Copy the metadata file to the container
    copy_command = f"kubectl cp {metadataFile_path} {namespace}/{pod_name}:/opt/payara/dvinstall/data/metadatablocks/{metadataFile} -c {containername}"
    os.system(copy_command)
    print(containerID)
    # Upload metadata
    if apiBlocked == True:
        upload_metadata_command = (
            f"docker exec -u root {containerID} curl http://localhost:8080/api/admin/datasetfield/load -H \"Content-type: text/tab-separated-values\" -X POST --upload-file /opt/payara/dvinstall/data/metadatablocks/{metadataFile}"
        )

    elif apiBlocked == False:
        upload_metadata_command  = (
            f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
            f"curl http://localhost:8080/api/admin/datasetfield/load -H \"Content-type: text/tab-separated-values\" -X POST --upload-file /opt/payara/dvinstall/data/metadatablocks/{metadataFile}"
        )
    # Run command to upload metadata
    os.system(upload_metadata_command)

    command = (
            f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
            f"curl 'http://localhost:8080/api/admin/index/solr/schema' | /opt/payara/dvinstall/update-fields.sh /opt/payara/dvinstall/schema.xml"
            # f"curl 'http://localhost:8080/api/admin/index/solr/schema' | tac | tac | ./update-fields.sh /opt/payara/dvinstall/schema.xml"
        )
    subprocess.run(command, shell=True)

    # Reload solr collection to make
    pod_name, containerID
    solr_pod_name, solr_container_id = get_pod_name_by_deployment("solr", namespace, "solr")

    command = (
            f"docker exec {solr_container_id} curl \"http://localhost:8983/solr/admin/cores?action=RELOAD&core=collection1\""
        )
    os.system(command)

else:
    print(f"No pod found for deployment '{deployment_name}'.")
