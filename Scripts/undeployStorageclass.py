import os

#old
# os.system("kubectl config set-context --current --namespace=kube-system")
# os.system("helm delete nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner")
# os.system("kubectl config set-context --current --namespace=dv-test")


# new
os.system("kubectl config set-context --current --namespace=kube-system")
os.system("kubectl delete storageclass csi-nfs")
os.system("helm delete csi-driver-nfs csi-driver-nfs/csi-driver-nfs")
os.system("kubectl config set-context --current --namespace=dv-test")