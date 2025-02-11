import os

#old
# os.system("kubectl config set-context --current --namespace=kube-system")
# os.system("helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner     --set nfs.server=141.19.44.16 --set nfs.path=/export/dataverse-pvs")
# os.system("kubectl config set-context --current --namespace=dv-test")


# new
os.system("helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts")
os.system("""helm install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
              --namespace kube-system \
              --set externalSnapshotter.enabled=true \
              --set storageClass.create=false \
              --set storageClass.name=csi-nfs \
              --set storageClass.provisioner=nfs.csi.k8s.io \
              --set storageClass.parameters.server=141.19.44.16 \
              --set storageClass.parameters.share=/export/dataverse-pvs
            """)
os.system("kubectl apply -f k8s/storageclass/storageclass.yaml")
