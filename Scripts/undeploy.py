import os
# be aware all persistent volumes get deleted with this!!!!

# change path
os.chdir("..")

# add command to import secret for registry in namespace

os.system("kubectl delete -f k8s/dataverse/jobs/bootstrap.yaml")
os.system("kubectl delete -f k8s/dataverse/jobs/configure.yaml")
os.system("kubectl delete -k prod-skel/envs/env1")
os.system("kubectl delete -f prod/secrets/secrets.yaml")
# os.system("kubectl delete -f prod-skel/storageClass.yaml")
# os.system("docker container prune -f")
print("Undeploy Dataverse")






