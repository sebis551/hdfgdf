import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(user_id, role = "user"):
    payload = {
        "user_id": user_id,
        "role": role,
        "iss": "my-secret-key",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None 