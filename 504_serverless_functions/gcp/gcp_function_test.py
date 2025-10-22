import requests

url = "https://serverless504-543241179392.europe-west1.run.app"

body = {
    "hba1c": 6.0
}

response = requests.post(url, json=body)

print(response.status_code)
print(response.text)