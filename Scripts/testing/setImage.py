import os
from kubernetes import client, config
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

def resize_image(original_image_path, resized_image_path):
    with Image.open(original_image_path) as image:
        resized_image = image.resize((160, 50))
        resized_image.save(resized_image_path)

def resize_svg(original_svg_path, resized_svg_path):
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

# change directory inside container to make logo persistent

# Usage
deployment_name = "dataverse"
namespace = "dv-test"  # Replace with the appropriate namespace
containername = "dataverse"
imagename = "TransparentLogo.svg"
apiBlocked = True

pod_name, containerID = get_pod_name_by_deployment(deployment_name, namespace, containername)
print(os.getcwd())
if pod_name:
    print(f"The pod name created by deployment '{deployment_name}' is '{pod_name}'.")

    # Resize the image
    original_image_path = "../img/" + imagename
    resized_image_path = "resized_" + imagename

    # Determine the file type based on the extension
    extension = os.path.splitext(imagename)[1].lower()

    if extension in ['.jpg', '.jpeg', '.png']:
        resize_image(original_image_path, resized_image_path)
    elif extension == '.svg':
        resize_svg(original_image_path, resized_image_path)

    # Copy the resized image to the container
    copy_command = f"kubectl cp {resized_image_path} {namespace}/{pod_name}:/opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/logos/{imagename} -c {containername}"
    os.system(copy_command)

    # # copy image in required directory
    # symbolic_link_command = (
    #     f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
    #     f"cp /opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/logos/{imagename} /opt/payara/appserver/glassfish/domains/domain1/applications/dataverse/{imagename}"
    # )
    # os.system(symbolic_link_command)

    # Change the logo
    if apiBlocked == True:
        # change_logo_command = (
        #     f"docker exec -u root {containerID} curl -X PUT -d logos/{imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
        # )
        change_logo_command = (
            f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
            f"curl -X PUT -d logos/{imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
        )

    elif apiBlocked == False:
        change_logo_command = (
            f"kubectl exec -n {namespace} pod/{pod_name} -c {containername} -- "
            f"curl -X PUT -d logos/{imagename} http://localhost:8080/api/admin/settings/:LogoCustomizationFile"
        )
    # Run command to change logo
    os.system(change_logo_command)

    # Clean up the resized image file
    os.remove(resized_image_path)
else:
    print(f"No pod found for deployment '{deployment_name}'.")
