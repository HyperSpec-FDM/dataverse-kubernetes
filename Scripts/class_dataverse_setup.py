import os
import subprocess
import requests
from kubernetes import client, config
from kubernetes.stream import stream
import time
import zipfile
from PIL import Image
from xml.etree import ElementTree as ET
class dataverse_setuper():
    def __init__(self, deployment_name, namespace, container_name, url):
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.container_name = container_name
        self.url = url

        # Load the Kubernetes configuration
        config.load_kube_config()

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

    def resize_image(self, original_image_path, resized_image_path):
        with Image.open(original_image_path) as image:
            resized_image = image.resize((160, 50))
            resized_image.save(resized_image_path)

    def resize_svg(self, original_svg_path, resized_svg_path):
        # Resize SVG files by modifying XML structure
        with open(original_svg_path, "r") as file:
            svg_content = file.read()

        # Parse the SVG content into an XML tree
        root = ET.fromstring(svg_content)

        # Modify the width and height attributes of the root SVG element
        root.set("width", "160")
        root.set("height", "50")

        # Generate the modified SVG content
        modified_svg_content = ET.tostring(root, encoding="unicode")

        # Write the modified SVG content to a new file
        with open(resized_svg_path, "w") as file:
            file.write(modified_svg_content)

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

    def get_users(self):
        # Get the pod name for the PostgreSQL deployment
        postgresql_pod_name, postgresql_container_id = self.get_pod_name_by_deployment("postgresql", self.namespace,
                                                                                       "postgresql")
        # Define the SQL command to fetch users and their superuser status
        sql_command = "SELECT * FROM public.authenticateduser;"
        # Execute the SQL command in the PostgreSQL pod and capture the output
        output = self.pod_exec(postgresql_pod_name, "postgresql", namespace, f'psql -c "{sql_command}"',
                               capture_output=True)
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
        return users

    def compare_users(self, users_before, users_after):

        # Create a dictionary where the 'useridentifier' is the key and the entire dictionary is the value
        dict1 = {item['useridentifier']: item for item in users_before}
        dict2 = {item['useridentifier']: item for item in users_after}

        # Find the differences based on 'superuser' values
        differences = []
        for key in dict1:
            if key in dict2 and dict1[key]['superuser'] != dict2[key]['superuser']:
                differences.append((key, dict1[key]['superuser'], dict2[key]['superuser']))

    def change_logo(self, imagename):
        if self.pod_name:
            # Resize the image
            original_image_path = "../img/" + imagename
            resized_image_path = "resized_" + imagename

            # Determine the file type based on the extension
            extension = os.path.splitext(imagename)[1].lower()
            if extension in ['.jpg', '.jpeg', '.png']:
                self.resize_image(original_image_path, resized_image_path)
            elif extension == '.svg':
                self.resize_svg(original_image_path, resized_image_path)

            # Create directory inside the dataverse container
            create_dir_command = "mkdir /opt/docroot/logos"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, create_dir_command)

            # Copy the resized image to the container in persistent directory
            copy_command = f"kubectl cp {resized_image_path} {self.namespace}/{self.pod_name}:/opt/docroot/logos/{imagename} -c {self.container_name}"
            os.system(copy_command)

            # Copy the resized image in required directory
            # copy_command = f"cp /opt/docroot/logos/{imagename} /opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/{imagename}"
            copy_command = f"cp /opt/docroot/logos/{imagename} /opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/resources/images/{imagename}"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, copy_command)

            # Change the logo of dataverse
            # copy_command = f"curl -X PUT -d {imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
            copy_command = f"curl -X PUT -d /resources/images/{imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, copy_command)

            # Clean up the resized image file
            os.remove(resized_image_path)

        else:
            print(f"No pod found for deployment '{deployment_name}'.")

    def add_custom_metadata(self, metadataFile):
        if self.pod_name:
            # Custom metadata
            metadataFile_path = "../metadata/" + metadataFile

            # Copy the metadata file to the container
            copy_command = f"kubectl cp {metadataFile_path} {self.namespace}/{self.pod_name}:/opt/payara/dvinstall/data/metadatablocks/{metadataFile} -c {self.container_name}"
            os.system(copy_command)

            # Upload metadata
            upload_metadata_command = f"curl http://localhost:8080/api/admin/datasetfield/load -H \"Content-type: text/tab-separated-values\" -X POST --upload-file /opt/payara/dvinstall/data/metadatablocks/{metadataFile}"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, upload_metadata_command)

            # Update index
            update_index_command = f"curl 'http://localhost:8080/api/admin/index/solr/schema' | /opt/payara/dvinstall/update-fields.sh /opt/payara/dvinstall/schema.xml"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, update_index_command)

            # Reload solr collection to make
            solr_pod_name, solr_container_id = self.get_pod_name_by_deployment("solr", self.namespace, "solr")

            reload_collection_command = f"curl \"http://localhost:8983/solr/admin/cores?action=RELOAD&core=collection1\""
            self.pod_exec(solr_pod_name, "solr", self.namespace, reload_collection_command)

        else:
            print(f"No pod found for deployment '{deployment_name}'.")

    # def remove_custom_metadata(self, name):
    #     # nicht nutzen, macht die ganze instand unbrauchbar!!
    #     pass
    #     # Get postgresql pod
    #     postgresql_pod_name, postgresql_container_id = self.get_pod_name_by_deployment("postgresql", self.namespace, "postgresql")
    #
    #     # Define sql command
    #     sql_command = f"""SELECT id
    #                       FROM public.datasetfieldtype
    #                       WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = '{name}');
    #
    #                       ALTER TABLE public.datasetfieldtype
    #                       DROP CONSTRAINT fk_datasetfieldtype_parentdatasetfieldtype_id;
    #
    #                       UPDATE public.datasetfieldtype
    #                       SET metadatablock_id = NULL
    #                       WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = '{name}');
    #
    #                       DELETE FROM public.datasetfieldtype WHERE metadatablock_id IS NULL;
    #                       DELETE FROM public.metadatablock WHERE name = '{name}';
    #                       SELECT SETVAL(pg_get_serial_sequence('public.metadatablock', 'id'), (SELECT MAX(column_name) FROM public.metadatablock));
    #
    #                       ALTER TABLE public.datasetfieldtype
    #                       ADD CONSTRAINT fk_datasetfieldtype_parentdatasetfieldtype_id
    #                       FOREIGN KEY (id)
    #                       REFERENCES public.datasetfieldtype(id);
    #                         """
    #
    #     self.pod_exec(postgresql_pod_name, "postgresql", self.namespace, f'psql -c "{sql_command}"')

    def add_languages(self, languages):
        if self.pod_name:
            # Run Container script to add new languages
            languageString = (" ".join(languages))
            command = f"./scripts/addLanguages.sh {languageString}"
            self.pod_exec(self.pod_name, self.container_name, self.namespace, command)

        else:
            print(f"No pod found for deployment '{deployment_name}'.")

    def set_superuser(self, user, value=True):
        # Get postgresql pod
        postgresql_pod_name, postgresql_container_id = self.get_pod_name_by_deployment("postgresql", self.namespace, "postgresql")

        # Define sql command
        sql_command = f"""UPDATE public.authenticateduser
                          SET "superuser" = {value}
                          WHERE "useridentifier" = '{user}';"""
        # sql_command = f"psql -c \"{sql_command}\""

        self.pod_exec(postgresql_pod_name, "postgresql", self.namespace, f'psql -c "{sql_command}"')

    def add_s3_storage(self, lable, bucketname, profile, accessKey, secretKey, endpoint, changePostgres = True):
        # Set variable for script path to add new storage
        script_path = "/opt/payara/scripts/newS3Storage.sh"

        # Create variables for jvm-options and enviroment variables
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

        # Set variables for later usage
        status = None
        old_pod_status = None

        users = self.get_users()

        # Set old pod name
        old_pod_name = self.pod_name

        # Get the deployment
        deployment = self.apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        # Update the environment variable in each container
        for container in deployment.spec.template.spec.containers:
            for env in env_vars:
                if container.env is None:
                    container.env = []
                container.env.append(client.V1EnvVar(name=env["name"], value=env["value"]))

        # Patch the deployment to apply the changes
        self.apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )

        # Update Postgresql table
        if changePostgres == True:
            # Wait for old_pod to be stopped
            while old_pod_status != "Stopped":
                # Get old pod status
                old_pod_status = self.get_pod_status(old_pod_name, namespace)
                print("Waiting for old dataverse pod to be stopped...")
                time.sleep(5)

            # Wait for dataverse to be ready before changing superuser attribute
            while status != 200:
                try:
                    resp = requests.get(self.url)
                    status = resp.status_code
                except:
                    time.sleep(5)

            while True:
                for user in users:
                    if user["superuser"] == "t":
                        self.set_superuser(user["useridentifier"], True)
                # Extract users from postgres and check if all differences are eliminated
                users_new = self.get_users()
                print(users_new)
                differences = self.compare_users(users, users_new)
                if not differences:
                    break

            # Get new pod and run jvm resources
            pod_name, pod_id = self.get_pod_name_by_deployment(deployment_name, self.namespace, self.container_name)
            self.pod_name = pod_name

            # Wait for the container to be ready before executing commands
            self.wait_for_container_ready(pod_name, container_name, namespace, self.core_v1)

            # Create directory if not present to store information for every added storage
            command = f"mkdir /opt/docroot/s3"
            self.pod_exec(pod_name, container_name, namespace, command)

            # Safe Information in that directory
            command = f"echo {variables} > /opt/docroot/s3/{lable}"
            self.pod_exec(pod_name, container_name, namespace, command)

            # Create command for jvm resource creation
            command = f"{script_path} $(cat /opt/docroot/s3/{lable} | tr -d '[],')"

            # create jvm resources
            self.pod_exec(pod_name, container_name, namespace, command)

    def setup_shibboleth(self, api_key, persistent_id):
        delete_command = f"curl -I -H 'X-Dataverse-key: {api_key}' -X DELETE \"http://localhost:8080/api/datasets/:persistentId/destroy/?persistentId={persistent_id}\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, delete_command)

    def delete_dataverse(self, api_key, persistent_id):
        delete_command = f"curl -I -H 'X-Dataverse-key: {api_key}' -X DELETE \"http://localhost:8080/api/dataverses/{persistent_id}\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, delete_command)

    def delete_dataset(self, api_key, persistent_id):
        delete_command = f"curl -I -H 'X-Dataverse-key: {api_key}' -X DELETE \"http://localhost:8080/api/datasets/:persistentId/destroy/?persistentId={persistent_id}\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, delete_command)

    def curl_dataverse(self, api_key, dataverse_id):
        curl_command = f"curl -H 'X-Dataverse-key: {api_key}' \"http://localhost:8080/api/dataverses/{dataverse_id}/contents\""
        self.pod_exec(self.pod_name, self.container_name, self.namespace, curl_command)


deployment_name = "dataverse"
namespace = "dv-test"  # Replace with the appropriate namespace
container_name = "dataverse"
url = "http://192.168.100.11:30000" + "/robots.txt"
imagename = "TransparentLogo.svg"
metadata_file = "addition_citation.tsv" #"citation.tsv"
# languages = ['de_AT', 'de_DE', 'en_US', 'es_ES', 'fr_CA', 'fr_FR', 'hu_HU', 'it_IT', 'pl_PL', 'pt_BR', 'pt_PT', 'ru_RU', 'se_SE', 'sl_SI', 'ua_UA']
languages = ['en_US', 'de_DE']
api_key = "5624a1d8-0f9b-4c8d-ad71-318f6e303fd3"
persistent_id = "doi:10.12345/EXAMPLE/H7RRWR"



tt = dataverse_setuper(deployment_name, namespace, container_name, url)

# tt.change_logo(imagename)
# tt.add_custom_metadata(metadata_file)
# tt.remove_custom_metadata("hyperspec-fdm")
# tt.add_languages(languages)
# tt.set_superuser("dataverseAdmin", True)
tt.add_s3_storage("hyperspec-fdm", "hyperspec-fdm", "minio_profile_1", "Vfzf1byfPPLRyNTF0Lzn", "9yPhiXscdVhIwrWO3oIVrqAOpIFeUt1gqmnFAWUR", "http\:\/\/141.19.44.16\:9000")

# tt.delete_dataset(api_key, persistent_id)
# tt.curl_dataverse(api_key, "HyperSpec-FDM")
# tt.delete_dataverse(api_key, "")


