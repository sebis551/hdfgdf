import requests

DB_SERVICE_URL = "http://db-service:5002"

def create_user(username, password):
    resp = requests.post(f"{DB_SERVICE_URL}/users", json={"username": username, "password": password})
    if resp.status_code == 201:
        return resp.json()
    return None

def authenticate_user(username, password):
    resp = requests.post(f"{DB_SERVICE_URL}/users/auth", json={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()
    return None
