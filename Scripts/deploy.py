import os

# change path
os.chdir("..")

# deploy secrets and dataverse enviroment
os.system("kubectl apply -f prod-skel\secrets")
os.system("kubectl apply -k prod-skel\envs\env1")
os.system("kubectl create -f k8s/dataverse/jobs/bootstrap.yaml")


# deploy s3
os.system("kubectl apply -f prod-skel/bases/minio-standalone/pvc.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/svc.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/config.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/deployment.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/job.yaml")
