import os

# Define Dataverse Dockerfile, Version and Tag
dockerfileDataverse = "./docker/dataverse-k8s/payara/Dockerfile"
versionDataverse = "5.14"
tagDataverse = "iqss/dataverse-k8s:" + versionDataverse

# Define Solr Dockerfile, Version and Tag
dockerfileSolr = "./docker/solr-k8s/Dockerfile"
versionSolr = "8.11.1"
tagSolr = "iqss/solr-k8s:" + versionSolr

# Define privat registry endpoint
registry = "192.168.100.11:31000"
user = "tim"
password = "changeme"

# Define which image to build and push
dataverse = True
solr = False
pushonly = False

# Change working directory
os.chdir("..")


def buildImage(dockerfile, tag):
    buildCommand = f"docker build --no-cache -t {tag} -f {dockerfile} ."
    os.system(buildCommand)

def pushToRegistry(imageTag, registry):
    loginCommand = f"docker login -u {user} -p {password} 192.168.100.11:31000"
    os.system(loginCommand)
    tagCommand = f"docker tag {imageTag} {registry}/{imageTag}"
    os.system(tagCommand)
    pushCommand =f"docker push {registry}/{imageTag}"
    print(pushCommand)
    os.system(pushCommand)


# Build the desired image or images and push to local registry
if dataverse and solr:
    if not pushonly:
        buildImage(dockerfileDataverse, tagDataverse)
        buildImage(dockerfileSolr, tagSolr)
    pushToRegistry(tagDataverse, registry)
    pushToRegistry(tagSolr, registry)
elif dataverse:
    if not pushonly:
        buildImage(dockerfileDataverse, tagDataverse)
    pushToRegistry(tagDataverse, registry)
elif solr:
    if not pushonly:
        buildImage(dockerfileSolr, tagSolr)
    pushToRegistry(tagSolr, registry)
else:
    print("No image to build..")


