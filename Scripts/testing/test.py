import requests



api_token = "9f192cf5-53f1-4cfc-912a-ae7bfbe8e94b"
dataverse = "Root"
headers = {"X-Dataverse-key": api_token}
url = f"http://localhost:8080/api/dataverses/{dataverse}"

resp = requests.get(url, headers)
print(resp.json())