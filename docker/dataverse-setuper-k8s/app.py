from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi import Query
import uvicorn
from class_dataverse_setup import dataverse_setuper
import os
import json
import typing


# retrieve variables from environment
# deployment_name = os.environ["deployment_name"]
# namespace = os.environ["namespace"]
# container_name = os.environ["container_name"]
# dataverse_url = os.environ["dataverse_url"] +  "/robots.txt"
deployment_name = "dataverse"
namespace = "dv-test"  # Replace with the appropriate namespace
container_name = "dataverse"
dataverse_url = "http://192.168.100.11:30000" + "/robots.txt"

# define directory variables
img_dir = "./img"
metadata_dir = "./metadata"

# define allowed languages
allowed_languages = ['de_AT', 'de_DE', 'en_US', 'es_ES', 'fr_CA', 'fr_FR', 'hu_HU', 'it_IT', 'pl_PL', 'pt_BR', 'pt_PT', 'ru_RU', 'se_SE', 'sl_SI', 'ua_UA']


# create inctance of dataverse_setuper
setuper = dataverse_setuper(deployment_name=deployment_name, namespace=namespace, container_name=container_name, url=dataverse_url)


"""create API"""
rootPath = "/dtps"
App = FastAPI()

"""define API Methods"""
@App.post("/change_logo")
async def change_logo(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(f"{img_dir}/{file.filename}", 'wb') as f:
            f.write(contents)

    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    try:
        setuper.change_logo(img_dir, file.filename)
        return {"message": f"Successfully changed dataverse logo to {file.filename}"}
    except:
        return {"message": "Failed to change dataverse logo"}

@App.delete("/remove_logo")
async def remove_logo():
    setuper.remove_logo()
    return {"message": "Removed Custom logo."}

@App.post("/add_custom_metadata")
async def add_custom_metadata(file: UploadFile = File(...)):
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
        setuper.change_logo(metadata_dir, file.filename)
        return {"message": f"Successfully changed dataverse logo to {file.filename}"}
    except:
        return {"message": "Failed to change dataverse logo"}


@App.post("/add_languages")
async def add_languages(languages: typing.Annotated[list, Query()]):
    exchange_dict = {"allowed": [], "denied": []}

    for item in languages:
        if item in allowed_languages:
            exchange_dict["allowed"].append(item)
        else:
            exchange_dict["denied"].append(item)

    # remove potential duplicates
    exchange_dict["allowed"] = list(set(exchange_dict["allowed"]))
    exchange_dict["denied"] = list(set(exchange_dict["denied"]))


    if exchange_dict["allowed"] == []:
        return {"message": f"Failed to add languages {', '.join(lang for lang in exchange_dict['denied'])}. Only {', '.join(lang for lang in allowed_languages)} are allowed!"}
    elif exchange_dict["denied"] == []:
        # setuper.add_languages(exchange_dict["allowed"])
        return {"message": f"Added languages {', '.join(lang for lang in exchange_dict['allowed'])}."}
    else:
        # setuper.add_languages(exchange_dict["allowed"])
        return {"message": f"Added languages {', '.join(lang for lang in exchange_dict['allowed'])}. Failed to add languages {', '.join(lang for lang in exchange_dict['denied'])}. Only {', '.join(lang for lang in allowed_languages)} are allowed!"}

@App.post("/set_superuser")
async def set_superuser(user, value: bool = True):
    # check if user exists
    exists = setuper.check_user_exist(user).replace("case", "").replace("-", "").replace("(1 row)", "").replace("\n", "").replace(" ", "")
    exists = json.loads(exists.lower())

    if exists == True:
        setuper.set_superuser(user, value)
        return {"message": f"Set super user privileges for user {user} to {value}."}
    else:
        return {"message": f"Failed! User {user} does not exist!"}

@App.post("/add_s3")
async def add_s3(lable, bucketname, profile, accessKey, secretKey, endpoint):
    # check if label is already in use
    labels = setuper.check_s3_labels()

    if lable not in labels:
        setuper.add_s3_storage(lable=lable, bucketname=bucketname, profile=profile, accessKey=accessKey, secretKey=secretKey, endpoint=endpoint)
        return {"message": f"Added S3 Storage with label {lable}."}

    else:
        return {"message": f"Failed to add S3! Label {lable} does already exist!"}

@App.post("/add_mail")
async def add_mail(host, mail, password, overwrite: bool = False):
    if "@" not in mail:
        return {"message": f"Error! Please provide a valid email address."}

    # check if mail session already exists
    files = setuper.check_mail()

    if files == []:
        setuper.add_mail( host, mail, password)
        return {"message": f"Added mail {mail}."}
    elif overwrite == True:
        setuper.remove_mail()
        setuper.add_mail(host, mail, password)
        return {"message": f"Added mail {mail}."}
    else:
        return {"message": f"Mail already set, use overwrite=True to overwrite."}

@App.post("/add_shibboleth")
async def add_shibboleth():
    setuper.add_shibboleth()
    return {"message": f"Added Shibboleth Authentication Provider."}

@App.delete("/remove_shibboleth")
async def remove_shibboleth():
    setuper.remove_shibboleth()
    return {"message": f"Removed Shibboleth Authentication Provider."}


"""rund API server. swagger ui on http://127.0.0.1:8000/docs#/"""
uvicorn.run(App, host="0.0.0.0", port=8000, log_level="info")
