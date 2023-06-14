import os
import time
import requests


# set url for dataverse
url = "http://localhost:8080/robots.txt"
status = None

# change path
os.chdir("..")

# deploy secrets and dataverse enviroment
os.system("kubectl apply -f prod-skel\secrets")
os.system("kubectl apply -k prod-skel\envs\env1")
os.system("kubectl create -f k8s/dataverse/jobs/bootstrap.yaml")

# # check if dataverse is running
# while status != 200:
#     try:
#         resp = requests.get(url)
#         status = resp.status_code
#     except requests.exceptions.RequestException as e:
#         print("Waiting for Dataverse to start...")
#         time.sleep(10)
#
# # create bootstrap job configure dataverse
# try:
#     os.system("kubectl create -f k8s/dataverse/jobs/bootstrap.yaml")
# except:
#     print("bootstrap already running")
#
# print("Deployed Dataverse on Kubernetes")

