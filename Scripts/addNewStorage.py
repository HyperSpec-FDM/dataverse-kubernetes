from kubernetes import client, config
from kubernetes.stream import stream
import requests
from itertools import zip_longest as zip
import time

def is_container_ready(pod):
    for condition in pod.status.conditions:
        if condition.type == "Ready" and condition.status == "True":
            return True
    return False

def wait_for_container_ready(pod_name, container_name, namespace, api_instance):
    while True:
        try:
            pod = api_instance.read_namespaced_pod(pod_name, namespace)
            if pod.status.phase != "Running":
                time.sleep(1)
                continue
            container_statuses = pod.status.container_statuses
            for status in container_statuses:
                if status.name == container_name and status.ready:
                    return
        except Exception as e:
            time.sleep(1)
            continue
        time.sleep(1)

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
env_vars = [
            {'name': f'dataverse_files_{lable}_type', 'value': 's3'},
            {'name': f'dataverse_files_{lable}_label', 'value': f'{lable}'},
            {'name': f'dataverse_files_{lable}_bucket__name', 'value': f'{bucketname}'},
            {'name': f'dataverse_files_{lable}_download__redirect', 'value': 'false'},
            {'name': f'dataverse_files_{lable}_url__expiration__minutes', 'value': '120'},
            {'name': f'dataverse_files_{lable}_connection__pool__size', 'value': '4096'},
            {'name': f'dataverse_files_{lable}_profile', 'value': f'{profile}'},
            {'name': f'dataverse_files_{lable}_custom__endpoint__url', 'value': f'{endpoint}'},
            {'name': f'dataverse_files_{lable}_path__style__access', 'value': 'true'},
            {'name': f'dataverse_files_{lable}_access__key', 'value': f'{accessKey}'},
            {'name': f'dataverse_files_{lable}_secret__key', 'value': f'{secretKey}'}]



# set url for dataverse
url = "http://localhost:8080/robots.txt"
status = None
old_pod_status = None

# Load Kubernetes configuration from default location
config.load_kube_config()

# Create an instance of the CoreV1Api
api = client.CoreV1Api()
api_patch = client.AppsV1Api()

# Get the pod name for the PostgreSQL deployment
postgresql_pod_name = get_pod_name_by_deployment("postgresql", namespace)

# Define the SQL command to fetch users and their superuser status
sql_command = "SELECT * FROM public.authenticateduser;"

# Execute the SQL command in the PostgreSQL pod and capture the output
output = pod_exec(postgresql_pod_name, "postgresql", namespace, f'psql -c "{sql_command}"', api, capture_output=True)

# Split the text into rows
headers = output.strip().split("\n")[0:1]  # get header line
lines = output.strip().split("\n")[2:-1]  # get remaining lines without the last on (rows:x)

# Extract column names from the header row
headers = [name.strip() for name in headers[0].split("|")]

users = []

for line in output.strip().split("\n")[2:-1]:
    lineList = line.split("|")
    lineList = [item.replace(" ", "") for item in lineList]
    merged = dict(zip(headers, lineList))
    users.append(merged)


# Get pod name from deployment
pod_name = get_pod_name_by_deployment(deployment_name, namespace)
old_pod_name = pod_name

# Get the deployment
deployment = api_patch.read_namespaced_deployment(name=deployment_name, namespace=namespace)

# Update the environment variable in each container
for container in deployment.spec.template.spec.containers:
    for env in env_vars:
        if container.env is None:
            container.env = []
        container.env.append(client.V1EnvVar(name=env["name"], value=env["value"]))


# Patch the deployment to apply the changes
api_patch.patch_namespaced_deployment(
    name=deployment_name,
    namespace=namespace,
    body=deployment
)

# Create jvm resources in new pod
# Get new pod and run jvm resources
pod_name = get_pod_name_by_deployment(deployment_name, namespace)

# Wait for the container to be ready before executing commands
wait_for_container_ready(pod_name, container_name, namespace, api)

# Create command for jvm resource creation
command = f"chmod +x {script_path1} && {script_path1} {' '.join(variables)}"

# create jvm resources
pod_exec(pod_name, container_name, namespace, command, api)


# Update Postgresql table
# Wait for old_pod to be stopped
while old_pod_status != "Stopped":
    try:
        # Get old pod object
        old_pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)
        old_pod_status = old_pod.status.conditions.sstatus
        time.sleep(5)
    except:
        old_pod_status = "Stopped"

# Wait for dataverse to be ready before changing superuser attribute
while status != 200:
    resp = requests.get(url)
    status = resp.status_code
    time.sleep(5)

for user in users:
    if user["superuser"] == "t":
        sql_command = f"""UPDATE public.authenticateduser
                          SET "superuser" = TRUE
                          WHERE "useridentifier" = '{user["useridentifier"]}';"""

        # Execute the SQL command in the PostgreSQL pod and capture the output
        pod_exec(postgresql_pod_name, "postgresql", namespace, f'psql -c "{sql_command}"', api,)
