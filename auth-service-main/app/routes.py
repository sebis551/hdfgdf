from flask import Blueprint, request, jsonify
from .models import create_user, authenticate_user
from .auth_utils import generate_token, decode_token

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user = create_user(data.get("username"), data.get("password"))
    if not user:
        return jsonify({"error": "User already exists"}), 409
    return jsonify({"message": "User created"}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = authenticate_user(data.get("username"), data.get("password"))
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    if "admin" in data.get("username"):
        token = generate_token(user["id"], "admin")
    else:
        token = generate_token(user["id"], "user")
    return jsonify({"token": token})

@auth_routes.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if payload:
        response = {
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
        return jsonify(response)
    return jsonify({"error": "Invalid or expired token"}), 401