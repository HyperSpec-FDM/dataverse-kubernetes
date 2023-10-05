from kubernetes import client, config
from kubernetes.stream import stream

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

def pod_exec(pod_name, container_name, namespace, command, api_instance, capture_output=False):
    exec_command = ["/bin/sh", "-c", command]

    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name=pod_name,
                  namespace=namespace,
                  container=container_name,
                  command=exec_command,
                  stderr=True,
                  stdout=True,
                  stdin=False,
                  tty=False,
                  _preload_content=False)

    output = ""
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            if capture_output:
                output += resp.read_stdout()
            else:
                print(f"STDOUT: \n{resp.read_stdout()}")
        if resp.peek_stderr():
            if capture_output:
                output += resp.read_stderr()
            else:
                print(f"STDERR: \n{resp.read_stderr()}")

    resp.close()

    if capture_output is True:
        return output

# Define variables
namespace = "dv-test"
useridentifier = "dataverseAdmin"
value = True
value = str(value)

# Load Kubernetes configuration from default location
config.load_kube_config()

# Create an instance of the CoreV1Api
api = client.CoreV1Api()
api_patch = client.AppsV1Api()

# Get the pod name for the PostgreSQL deployment
postgresql_pod_name = get_pod_name_by_deployment("postgresql", namespace)

print(postgresql_pod_name)

sql_command = f"""UPDATE public.authenticateduser
                  SET "superuser" = {value}
                  WHERE "useridentifier" = '{useridentifier}';"""

# Execute the SQL command in the PostgreSQL pod and capture the output
pod_exec(postgresql_pod_name, "postgresql", namespace, f'psql -c "{sql_command}"', api,)