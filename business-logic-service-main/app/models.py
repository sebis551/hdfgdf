import requests

DB_SERVICE_URL = "http://db-service:5002"

def get_all_users(filters=None):
    params = filters if filters else {}
    resp = requests.get(f"{DB_SERVICE_URL}/profiles", params=params)
    return resp.json() if resp.status_code == 200 else []

def get_user_by_id(user_id):
    resp = requests.get(f"{DB_SERVICE_URL}/profiles/{user_id}")
    return resp.json() if resp.status_code == 200 else None

def add_user(data):
    resp = requests.post(f"{DB_SERVICE_URL}/profiles", json=data)
    return resp.json() if resp.status_code == 201 else None

def update_user(user_id, data):
    resp = requests.put(f"{DB_SERVICE_URL}/profiles/{user_id}", json=data)
    return resp.json() if resp.status_code in [200, 204] else None

def delete_user(user_id):
    resp = requests.delete(f"{DB_SERVICE_URL}/profiles/{user_id}")
    return resp.status_code == 204

def get_user_history(user_id):
    resp = requests.get(f"{DB_SERVICE_URL}/profiles/{user_id}/history")
    return resp.json() if resp.status_code == 200 else []
