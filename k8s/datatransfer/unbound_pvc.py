import os

pv_name = "pvc-33a24292-680b-4351-ac7f-44105742efc2"

os.system("kubectl patch pv " + pv_name + " -p '{\"spec\":{\"claimRef\": null}}'")