import os

# change path
os.chdir("..")

# create namespace for dataverse deployment
os.system("kubectl create namespace dv-test")

# import registry authentification secret
os.system('kubectl get secret registry-auth -n docker-registry -o yaml | sed s/"namespace: docker-registry"/"namespace: dv-test"/ | kubectl apply -n dv-test -f -')

# deploy secrets and dataverse enviroment
# os.system("kubectl apply -f prod-skel/secrets/")
os.system("kubectl apply -f prod-skel/secrets/secrets.yaml")
os.system("kubectl apply -k prod-skel/envs/env1")
# os.system("kubectl apply -f prod-skel/prod/mailcatcher.yaml")
os.system("kubectl apply -f k8s/shibboleth/deployment.yaml")
os.system("kubectl apply -f k8s/shibboleth/svc.yaml")

# os.system("kubectl create -f k8s/dataverse/jobs/bootstrap.yaml")

# deploy s3
# os.system("kubectl apply -f prod-skel/bases/minio-standalone/pvc.yaml")
# os.system("kubectl apply -f prod-skel/bases/minio-standalone/svc.yaml")
# os.system("kubectl apply -f prod-skel/bases/minio-standalone/config.yaml")
# os.system("kubectl apply -f prod-skel/bases/minio-standalone/deployment.yaml")
# os.system("kubectl apply -f prod-skel/bases/minio-standalone/job.yaml")

