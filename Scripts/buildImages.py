import os

# Define Dataverse Dockerfile, Version and Tag
dockerfileDataverse = "./docker/dataverse-k8s/payara/Dockerfile"
versionDataverse = "6.2"
tagDataverse = "iqss/dataverse-k8s:" + versionDataverse

# Define Solr Dockerfile, Version and Tag
dockerfileSolr = "./docker/solr-k8s/Dockerfile"
versionSolr = "9.3.0"
tagSolr = "iqss/solr-k8s:" + versionSolr

# Define Shibboleth Dockerfile, Version and Tag
dockerfileShibboleth = "./docker/shibboleth-k8s/Dockerfile"
versionShibboleth = "1.0"
tagShibboleth = "shibboleth:" + versionShibboleth

# Define Deleter Dockerfile, Version and Tag
dockerfileDeleter = "./docker/deleter-k8s/Dockerfile"
versionDeleter = "1.0"
tagDeleter = "dataverse_deleter:" + versionDeleter

# Define Dataverse Setuper Dockerfile, Version and Tag
dockerfileDataverseSetuper = "./docker/dataverse-setuper-k8s/Dockerfile"
versionDataverseSetuper = "1.0"
tagDataverseSetuper = "dataverse-setuper-k8s:" + versionDataverseSetuper

# Define keycloak-idp Dockerfile, Version and Tag
dockerfileKeycloakIdP = "./docker/keycloak-idp-k8s/Dockerfile"
versionKeycloakIdP = "1.0"
tagKeycloakIdP = "keycloak-idp-k8s:" + versionKeycloakIdP

# Define privat registry endpoint
registry = "192.168.100.11:31000"
user = "tim"
password = "changeme"

# Define which image to build and push
dataverse = True
solr = False
shibboleth = False
deleter = False
dataversesetuper = False
keycloakidp = False
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

# Clean up system to prevent full storage
cleancommand = "docker system prune -f"
os.system(cleancommand)

# Build the desired image or images and push to local registry
if dataverse == True:
    if not pushonly:
        buildImage(dockerfileDataverse, tagDataverse)
    pushToRegistry(tagDataverse, registry)
if solr == True:
    if not pushonly:
        buildImage(dockerfileSolr, tagSolr)
    pushToRegistry(tagSolr, registry)
if shibboleth == True:
    if not pushonly:
        buildImage(dockerfileShibboleth, tagShibboleth)
    pushToRegistry(tagShibboleth, registry)
if deleter == True:
    if not pushonly:
        buildImage(dockerfileDeleter, tagDeleter)
    pushToRegistry(tagDeleter, registry)
if dataversesetuper == True:
    if not pushonly:
        buildImage(dockerfileDataverseSetuper, tagDataverseSetuper)
    pushToRegistry(tagDataverseSetuper, registry)
if keycloakidp == True:
    if not pushonly:
        buildImage(dockerfileKeycloakIdP, tagKeycloakIdP)
    pushToRegistry(tagKeycloakIdP, registry)


