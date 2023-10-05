import os

os.system("kubectl config set-context --current --namespace=kube-system")
os.system("helm delete nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner")
os.system("kubectl config set-context --current --namespace=dv-test")