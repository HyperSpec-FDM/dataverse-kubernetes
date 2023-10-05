from kubernetes import client, config
import time

def restart_pod(pod_name, namespace):
    # Load Kubernetes configuration from default location
    config.load_kube_config()

    # Create an instance of the CoreV1Api
    api = client.CoreV1Api()

    try:
        # Get the pod object
        pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Delete the pod
        api.delete_namespaced_pod(name=pod_name, namespace=namespace, body=client.V1DeleteOptions())

    except Exception as e:
        print(f"Error while deleting pod {pod_name}: {e}")

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

# Define variables
namespace = "dv-test"
deployment_name = "dataverse"
container_name = "dataverse"

pod_name = get_pod_name_by_deployment(deployment_name, namespace)
restart_pod(pod_name, namespace)
