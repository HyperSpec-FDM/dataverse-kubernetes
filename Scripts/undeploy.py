import os


# change path
os.chdir("..")


os.system("kubectl delete -f k8s/dataverse/jobs/bootstrap.yaml")
os.system("kubectl delete -f k8s/dataverse/jobs/configure.yaml")
os.system("kubectl delete -k prod-skel\envs\env1")
os.system("kubectl delete -f prod/secrets.yaml")
os.system("docker container prune -f")
print("Undeploy Dataverse")


# undeploy s3
os.system("kubectl delete -f prod-skel/bases/minio-standalone/job.yaml")
os.system("kubectl delete -f prod-skel/bases/minio-standalone/deployment.yaml")
os.system("kubectl delete -f prod-skel/bases/minio-standalone/svc.yaml")
os.system("kubectl delete -f prod-skel/bases/minio-standalone/config.yaml")
os.system("kubectl delete -f prod-skel/bases/minio-standalone/pvc.yaml")





