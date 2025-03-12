import os

os.system("kubectl create job --from=cronjob/velero-backup-job velero-backup-now")