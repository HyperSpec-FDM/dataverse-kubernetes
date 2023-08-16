import os
import time
import requests

# set endpoint
url = "http://localhost:8080"
response_code = None

# change path
os.chdir("..")

# deploy secrets and dataverse enviroment
os.system("kubectl apply -f prod-skel\secrets")
os.system("kubectl apply -k prod-skel\envs\env1")

# deploy s3
os.system("kubectl apply -f prod-skel/bases/minio-standalone/pvc.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/svc.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/config.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/deployment.yaml")
os.system("kubectl apply -f prod-skel/bases/minio-standalone/job.yaml")

# # deploy jobs after dataverse is ready
# while response_code != 200:
#     resp = requests.get(url)
#     response_code = resp.status_code
#     time.sleep(15)
#
# os.system("kubectl create -f k8s/dataverse/jobs/bootstrap.yaml")

