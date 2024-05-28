import os

def add_custom_metadata(file):
    try:
        contents = file.file.read()
        extension = os.path.splitext(file.filename)[-1].lower()
        if extension == "tsv":
            with open(f"{metadata_dir}/{file.filename}", 'wb') as f:
                f.write(contents)
        else:
            return {"message": "Wrong file type. Only tsv allowed!"}

    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    try:
        # setuper.change_logo(metadata_dir, file.filename)
        return {"message": f"Successfully changed dataverse logo to {file.filename}"}
    except:
        return {"message": "Failed to change dataverse logo"}

f = "/home/tim/Documents/FDM/Dataverse-Kubernetes-Angepasst/metadata/addition_citation.tsv"

extension = os.path.splitext(f)[-1].lower()
print(extension)
# add_custom_metadata(f)