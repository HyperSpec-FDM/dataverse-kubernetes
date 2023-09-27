import os

os.system("kubectl config set-context --current --namespace=kube-system")
os.system("helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner     --set nfs.server=141.19.44.16 --set nfs.path=/export/dataverse-pvs")
os.system("kubectl config set-context --current --namespace=dv-test")