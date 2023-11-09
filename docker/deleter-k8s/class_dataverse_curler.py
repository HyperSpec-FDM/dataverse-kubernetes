from kubernetes import client, config
from kubernetes.stream import stream
import time

class dataverse_curler():
    def __init__(self, deployment_name, namespace, container_name, url, api_key):
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.container_name = container_name
        self.url = url
        self.api_key = api_key

        # Load the Kubernetes configuration
        config.load_incluster_config()

        # Create an instance of the Kubernetes AppsV1 API client
        self.apps_v1 = client.AppsV1Api()

        # Create an instance of the Kubernetes CoreV1 API client
        self.core_v1 = client.CoreV1Api()

        self.pod_name, self.containerID = self.get_pod_name_by_deployment(self.deployment_name, self.namespace, self.container_name)

    def get_pod_name_by_deployment(self, deployment_name, namespace, container_name):
        try:
            # Get the deployment object
            deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)

            # Get the labels selector for the deployment's pod template
            labels = deployment.spec.selector.match_labels

            # List pods in the same namespace with matching labels
            pods = self.core_v1.list_namespaced_pod(namespace,
                                               label_selector=','.join(f"{k}={v}" for k, v in labels.items())).items

            # Return the name of the first pod (assuming there is only one)
            if pods:
                for pod in pods:
                    # print(f"Containers in pod '{pod.metadata.name}':")
                    for container_status in pod.status.container_statuses:
                        name = container_status.name
                        container_id = container_status.container_id
                        if name == container_name:
                            cid = container_id.replace("docker://", "")
                return pods[0].metadata.name, cid
            else:
                return None
        except:
            return None

    def pod_exec(self, pod_name, container_name, namespace, command, capture_output=False):
        exec_command = ["/bin/sh", "-c", command]

        resp = stream(self.core_v1.connect_get_namespaced_pod_exec,
                      name=pod_name,
                      namespace=namespace,
                      container=container_name,
                      command=exec_command,
                      stderr=True,
                      stdout=True,
                      stdin=False,
                      tty=False,
                      _preload_content=False)

        output = {}
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                if capture_output:
                    output["STDOUT"] = resp.read_stdout()
                else:
                    print(f"STDOUT: \n{resp.read_stdout()}")
            if resp.peek_stderr():
                if capture_output:
                    output["STDERR"] = resp.read_stderr()
                else:
                    print(f"STDERR: \n{resp.read_stderr()}")
        resp.close()

        if capture_output is True:
            return output

    def get_pod_status(self, pod_name, namespace):
        while True:
            try:
                pod = self.core_v1.read_namespaced_pod(pod_name, namespace)
                return pod.status.phase
            except Exception as e:
                # print(f"Error while retrieving pod status: {e}")
                return "Stopped"

    def wait_for_container_ready(self, pod_name, container_name, namespace, api_instance):
        while True:
            try:
                pod = api_instance.read_namespaced_pod(pod_name, namespace)
                # print(pod.status.phase)
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

    def delete_dataverse(self, api_key, persistent_id):
        delete_command = f"curl -I -H 'X-Dataverse-key: {api_key}' -X DELETE \"http://localhost:8080/api/dataverses/{persistent_id}\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, delete_command)

    def delete_dataset(self, persistent_id):
        delete_command = f"curl -I -H 'X-Dataverse-key: {self.api_key}' -X DELETE \"http://localhost:8080/api/datasets/:persistentId/destroy/?persistentId={persistent_id}\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, delete_command)

    def curl_dataverse(self, dataverse_id):
        curl_command = f"curl -H 'X-Dataverse-key: {self.api_key}' \"http://localhost:8080/api/dataverses/{dataverse_id}/contents\""
        output = self.pod_exec(self.pod_name, self.container_name, self.namespace, curl_command, True)
        return output

    def curl_dataset(self, dataset_pid):
        curl_command = f"curl -H 'X-Dataverse-key: {self.api_key}' \"http://localhost:8080/api/datasets/:persistentId/versions/:draft?persistentId={dataset_pid}\""
        output = self.pod_exec(self.pod_name, self.container_name, self.namespace, curl_command, True)
        return output

