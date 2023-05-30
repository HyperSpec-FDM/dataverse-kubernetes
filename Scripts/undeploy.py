import os


# change path
os.chdir("..")


os.system("kubectl delete -f k8s/dataverse/jobs/bootstrap.yaml")
os.system("kubectl delete -k prod-skel\envs\env1")
os.system("kubectl delete -f prod/secrets.yaml")
os.system("docker container prune")
print("Undeploy Dataverse")


