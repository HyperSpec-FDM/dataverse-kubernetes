import os
from kubernetes import client, config
import zipfile

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
languages = ["en_US", "de_DE", "fr_FR"]
titles = {"en": "English", "de": "Deutsch", "fr": "Français"}
base_directory = "languages"
output_zip_filename = "languages.zip"

# change directory
os.chdir("../..")

# Create a zip file to write the selected files
with zipfile.ZipFile(output_zip_filename, 'w') as zipf:
    for directory in os.listdir(base_directory):
        if directory in languages:
            print(directory)
            directory_path = os.path.join(base_directory, directory)
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        arcname = os.path.basename(file_path)  # Use only the file name in the zip
                        zipf.writestr(arcname, file_content)

pod_name, containerID = get_pod_name_by_deployment(deployment_name, namespace, containername)

# Prepare dropdown content for curl command
dropdown = []
for lang in languages:
    locale, country = lang.split("_")
    dropdown.append({"locale": locale, "title": titles[locale]})

print(dropdown)

if pod_name:
    print(f"The pod name created by deployment '{deployment_name}' is '{pod_name}'.")

    # Create directory inside the dataverse container
    create_dir_command = (
        f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
        f"mkdir /opt/docroot/langBundles"
    )
    os.system(create_dir_command)

    # Copy zipfile to the container
    copy_command = f"kubectl cp {output_zip_filename} {namespace}/{pod_name}:/opt/docroot/langBundles/{output_zip_filename} -c {containername}"
    os.system(copy_command)

    # Enable languages
    enable_languages_command = (
        f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
        f"curl http://localhost:8080/api/admin/settings/:Languages -X PUT -d \"{dropdown}\""
    )
    os.system(enable_languages_command)
    enable_languages_command = (
        f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
        f"curl http://localhost:8080/api/admin/settings/:MetadataLanguages -X PUT -d \"{dropdown}\""
    )
    os.system(enable_languages_command)
    enable_languages_command = (
        f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
        f"asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile create-jvm-options \"-Ddataverse.lang.directory=/opt/docroot/langBundles\""
    )
    os.system(enable_languages_command)
    enable_languages_command = (
        f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
        f"curl http://localhost:8080/api/admin/datasetfield/loadpropertyfiles -X POST --upload-file /opt/docroot/langBundles/{output_zip_filename} -H \"Content-Type: application/zip\""
    )
    os.system(enable_languages_command)

    # Clean up the zipfile
    os.remove(output_zip_filename)
else:
    print(f"No pod found for deployment '{deployment_name}'.")