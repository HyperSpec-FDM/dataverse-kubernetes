import os
import subprocess
from kubernetes import client, config
from kubernetes.stream import stream

import zipfile
from PIL import Image
from xml.etree import ElementTree as ET
class dataverse_setuper():
    def __init__(self, deployment_name, namespace, container_name):
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.container_name = container_name
        self.titles = {"en": "English", "de": "Deutsch", "fr": "Français"}

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
                    print(f"Containers in pod '{pod.metadata.name}':")
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

            # Copy the resized image to the container
            copy_command = f"kubectl cp {resized_image_path} {self.namespace}/{self.pod_name}:/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/logos/{imagename} -c {self.container_name}"
            os.system(copy_command)

            # Change the logo of dataverse
            change_logo_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl -X PUT -d logos/{imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
            )
            os.system(change_logo_command)
            print(change_logo_command)

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
            upload_metadata_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl http://localhost:8080/api/admin/datasetfield/load -H \"Content-type: text/tab-separated-values\" -X POST --upload-file /opt/payara/dvinstall/data/metadatablocks/{metadataFile}"
            )
            # Run command to upload metadata
            os.system(upload_metadata_command)

            command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl 'http://localhost:8080/api/admin/index/solr/schema' | /opt/payara/dvinstall/update-fields.sh /opt/payara/dvinstall/schema.xml"
            )
            subprocess.run(command, shell=True)

            # Reload solr collection to make
            solr_pod_name, solr_container_id = self.get_pod_name_by_deployment("solr", self.namespace, "solr")
            print(solr_pod_name, solr_container_id)

            command = (
                f"docker exec {solr_container_id} curl \"http://localhost:8983/solr/admin/cores?action=RELOAD&core=collection1\""
            )
            # command = (
            #     f"kubectl exec -n {self.namespace} pod/{solr_pod_name} -c solr -- "
            #     f"curl \"http://localhost:8983/solr/admin/cores?action=RELOAD&core=collection1\""
            # )
            os.system(command)
        else:
            print(f"No pod found for deployment '{deployment_name}'.")

    def add_languages(self, languages, language_base_directory):
        if self.pod_name:
            # Set output name
            output_zip_filename = "languages.zip"

            # change directory
            os.chdir("..")

            # Create a zip file to write the selected files
            with zipfile.ZipFile(output_zip_filename, 'w') as zipf:
                for directory in os.listdir(language_base_directory):
                    if directory in languages:
                        print(directory)
                        directory_path = os.path.join(language_base_directory, directory)
                        for file in os.listdir(directory_path):
                            file_path = os.path.join(directory_path, file)
                            if os.path.isfile(file_path):
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                    arcname = os.path.basename(file_path)  # Use only the file name in the zip
                                    zipf.writestr(arcname, file_content)


            # Prepare dropdown content for curl command
            dropdown = []
            for lang in languages:
                locale, country = lang.split("_")
                dropdown.append({"locale": locale, "title": self.titles[locale]})

            print(dropdown)

            # Create directory inside the dataverse container
            create_dir_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"mkdir /opt/docroot/langBundles"
            )
            os.system(create_dir_command)

            # Copy zipfile to the container
            copy_command = f"kubectl cp {output_zip_filename} {self.namespace}/{self.pod_name}:/opt/docroot/langBundles/{output_zip_filename} -c {self.container_name}"
            os.system(copy_command)

            # Enable languages
            enable_languages_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl http://localhost:8080/api/admin/settings/:Languages -X PUT -d \"{dropdown}\""
            )
            os.system(enable_languages_command)
            enable_languages_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl http://localhost:8080/api/admin/settings/:MetadataLanguages -X PUT -d \"{dropdown}\""
            )
            os.system(enable_languages_command)
            enable_languages_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile create-jvm-options \"-Ddataverse.lang.directory=/opt/docroot/langBundles\""
            )
            os.system(enable_languages_command)
            enable_languages_command = (
                f"kubectl exec -n {self.namespace} pod/{self.pod_name} -c {self.container_name} -- "
                f"curl http://localhost:8080/api/admin/datasetfield/loadpropertyfiles -X POST --upload-file /opt/docroot/langBundles/{output_zip_filename} -H \"Content-Type: application/zip\""
            )
            os.system(enable_languages_command)

            # Clean up the zipfile
            os.remove(output_zip_filename)

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

    def add_s3_storage(self):


deployment_name = "dataverse"
namespace = "dv-test"  # Replace with the appropriate namespace
container_name = "dataverse"
imagename = "TransparentLogo.svg"


tt = dataverse_setuper(deployment_name, namespace, container_name)

# tt.change_logo(imagename)
# tt.add_custom_metadata("testmeta.tsv")
# tt.add_languages(["en_US", "de_DE", "fr_FR"], "languages")
# tt.set_superuser("dataverseAdmin", True)



