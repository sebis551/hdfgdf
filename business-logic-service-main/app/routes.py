from flask import Blueprint, jsonify, request
import requests
from .models import get_all_users, get_user_by_id, add_user, update_user, delete_user

user_routes = Blueprint('user_routes', __name__)
AUTH_SERVICE_URL = "http://auth-service:5001/verify-token"

def verify_token():
    token = request.headers.get("Authorization", "")
    if not token:
        return None
    try:
        response = requests.post(
            AUTH_SERVICE_URL,
            headers={"Authorization": token}
        )
        if response.status_code == 200:
            return response.json().get("user_id"), response.json().get("role")
    except:
        return None
    return None

# Rutele accesibile doar adminilor
@user_routes.route('/users', methods=['GET'])
def list_users():
    user_id_from_token, role_from_token = verify_token()
    
    if not user_id_from_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Permite doar accesul adminului la toți utilizatorii
    if role_from_token != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    name = request.args.get('name')
    min_steps = request.args.get('number_of_steps_min', type=int)
    min_distance = request.args.get('distance_traveled_min', type=float)
    min_age = request.args.get('age_min', type=int)

    users = get_all_users()
    if name:
        users = [u for u in users if name.lower() in u.get('name', '').lower()]
    if min_steps is not None:
        users = [u for u in users if u.get('number_of_steps', 0) >= min_steps]
    if min_distance is not None:
        users = [u for u in users if u.get('distance_traveled', 0.0) >= min_distance]
    if min_age is not None:
        users = [u for u in users if u.get('age', 0) >= min_age]

    return jsonify(users)

@user_routes.route('/users/<int:user_id>/history', methods=['GET'])
def user_history(user_id):
    user_id_from_token, role_from_token = verify_token()
    
    if not user_id_from_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Permite doar accesul utilizatorului la propriul istoric
    if user_id_from_token != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    from .models import get_user_history
    history = get_user_history(user_id)

    if history is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(history)

# Rutele accesibile pentru fiecare utilizator, doar pentru profilul propriu
@user_routes.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_id_from_token, role_from_token = verify_token()
    
    if not user_id_from_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Permite doar accesul utilizatorului la propriul profil
    if user_id_from_token != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    user = get_user_by_id(user_id)
    return jsonify(user) if user else (jsonify({"error": "Not found"}), 404)

@user_routes.route('/users', methods=['POST'])
def create_user():
    # Permite oricui să creeze un cont nou
    data = request.get_json()
    required = ("name", "age", "weight", "height", "heart_rhythm", "number_of_steps", "distance_traveled")
    if not all(k in data for k in required):
        return jsonify({"error": "Missing data"}), 400
    return jsonify(add_user(data)), 201

# Rutele accesibile doar adminilor
@user_routes.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    user_id_from_token, role_from_token = verify_token()
    
    if not user_id_from_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Permite doar adminilor să editeze orice profil
    if role_from_token != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.get_json()
    updated = update_user(user_id, data)
    if updated:
        return jsonify(updated), 200
    return jsonify({"error": "User not found or update failed"}), 404

@user_routes.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    user_id_from_token, role_from_token = verify_token()
    
    if not user_id_from_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Permite doar adminilor să șteargă orice profil
    if role_from_token != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    
    if delete_user(user_id):
        return '', 204
    return jsonify({"error": "User not found"}), 404
