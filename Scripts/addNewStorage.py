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

def pod_exec(pod_name, container_name, namespace, command, api_instance):
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

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print(f"STDOUT: \n{resp.read_stdout()}")
        if resp.peek_stderr():
            print(f"STDERR: \n{resp.read_stderr()}")

    resp.close()
    # if resp.returncode != 0:
    #     raise Exception("Script failed")

# Define variables
namespace = "dv-test"
deployment_name = "dataverse"
container_name = "dataverse"
script_path1 = "/opt/payara/scripts/newS3Storage.sh"
script_path2 = "/opt/payara/scripts/exportENV.sh"
lable = "hsma"
bucketname = "hsma"
profile = "minio_profile_1"
accessKey = "5IMXGis0YjH6620GIH16"
secretKey = "iJAI9HhY8RUW8RWjF0gt7lYZ9yxMKtFfuhlfrxLK"
endpoint = "http\:\/\/minio\:9000"
variables = [
    f"-Ddataverse.files.{lable}.type=s3",
    f"-Ddataverse.files.{lable}.label={lable}",
    f"-Ddataverse.files.{lable}.bucket-name={bucketname}",
    f"-Ddataverse.files.{lable}.download-redirect=false",
    f"-Ddataverse.files.{lable}.url-expiration-minutes=120",
    f"-Ddataverse.files.{lable}.connection-pool-size=4096",
    f"-Ddataverse.files.{lable}.profile={profile}",
    f'"-Ddataverse.files.{lable}.custom-endpoint-url\={endpoint}"',
    f"-Ddataverse.files.{lable}.path-style-access=true",
    f"-Ddataverse.files.{lable}.access-key={accessKey}",
    f"-Ddataverse.files.{lable}.secret-key={secretKey}"
]

# Load Kubernetes configuration from default location
config.load_kube_config()

# Create an instance of the CoreV1Api
api = client.CoreV1Api()
api_patch = client.AppsV1Api()

# Create command for jvm resource creation
command = f"chmod +x {script_path1} && {script_path1} {' '.join(variables)}"

# Get pod name from deployment
pod_name = get_pod_name_by_deployment(deployment_name, namespace)

# create jvm resources
pod_exec(pod_name, container_name, namespace, command, api)

# Get the deployment
deployment = api_patch.read_namespaced_deployment(name=deployment_name, namespace=namespace)

# Create command for env export
env_vars = []
for command in variables:
    if "-" in command:
        if command[0] == "-":
            command = command[1:]
        elif command[1] == "-":
            command = command[2:]
        command = command.replace("-", "__")
    if "\"" in command:
        command = command.replace("\"", "")
    if "\\" in command:
        command = command.replace("\\", "")
    if "D" in command:
        command = command.replace("D", "")
    command = command.replace(".", "_")
    env, value = command.split("=")
    env_vars.append({"name": env, "value": value})

    # Update the environment variable in each container
    for container in deployment.spec.template.spec.containers:
        if container.env is None:
            container.env = []
        container.env.append(client.V1EnvVar(name=env, value=value))

# Patch the deployment to apply the changes
api_patch.patch_namespaced_deployment(
    name=deployment_name,
    namespace=namespace,
    body=deployment
)