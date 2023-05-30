import os
from kubernetes import client, config


def get_pod_name_by_deployment(deployment_name, namespace):
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
        return pods[0].metadata.name
    else:
        return None

# Usage
deployment_name = "postgresql"
namespace = "dv-test"  # Replace with the appropriate namespace
containername = "postgresql"
containerCommand = "DELETE FROM setting WHERE name=':BlockedApiEndpoints';"

pod_name = get_pod_name_by_deployment(deployment_name, namespace)
if pod_name:
    print(f"The pod name created by deployment '{deployment_name}' is '{pod_name}'.")

    # unblock api
    osCommand = f"kubectl exec -n {namespace} pod/ {pod_name} -- psql -c \"{containerCommand}\""
    print(osCommand)
    os.system(osCommand)
else:
    print(f"No pod found for deployment '{deployment_name}'.")
