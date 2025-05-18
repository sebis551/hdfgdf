from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/fitnessdb'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    heart_rhythm = db.Column(db.Float)
    number_of_steps = db.Column(db.Integer)
    distance_traveled = db.Column(db.Float)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "weight": self.weight,
            "height": self.height,
            "heart_rhythm": self.heart_rhythm,
            "number_of_steps": self.number_of_steps,
            "distance_traveled": self.distance_traveled
        }

class UserProfileHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    heart_rhythm = db.Column(db.Float)
    number_of_steps = db.Column(db.Integer)
    distance_traveled = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "weight": self.weight,
            "height": self.height,
            "heart_rhythm": self.heart_rhythm,
            "number_of_steps": self.number_of_steps,
            "distance_traveled": self.distance_traveled,
            "timestamp": self.timestamp.isoformat()
        }

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        print(User.query)
        return jsonify({'error': 'User already exists'}), 409

    user = User(username=data['username'], password_hash=generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()

    return jsonify({'id': user.id, 'username': user.username}), 201

@app.route('/users/auth', methods=['POST'])
def authenticate_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        return jsonify({'id': user.id, 'username': user.username}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/profiles', methods=['GET'])
def get_all_profiles():

    query = UserProfile.query
    if 'name' in request.args:
        query = query.filter(UserProfile.name.ilike(f"%{request.args['name']}%"))
    if 'age' in request.args:
        query = query.filter_by(age=request.args.get('age'))
    if 'min_steps' in request.args:
        query = query.filter(UserProfile.number_of_steps >= int(request.args['min_steps']))
    if 'max_steps' in request.args:
        query = query.filter(UserProfile.number_of_steps <= int(request.args['max_steps']))
    if 'min_distance' in request.args:
        query = query.filter(UserProfile.distance_traveled >= float(request.args['min_distance']))
    if 'max_distance' in request.args:
        query = query.filter(UserProfile.distance_traveled <= float(request.args['max_distance']))

    users = query.all()
    return jsonify([u.as_dict() for u in users])

@app.route('/profiles/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = UserProfile.query.get(user_id)
    return jsonify(user.as_dict()) if user else ("", 404)

@app.route('/profiles', methods=['POST'])
def create_profile():
    data = request.get_json()
    user = UserProfile(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.as_dict()), 201

@app.route('/profiles/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = UserProfile.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    history = UserProfileHistory(
        user_id=user.id,
        weight=user.weight,
        height=user.height,
        heart_rhythm=user.heart_rhythm,
        number_of_steps=user.number_of_steps,
        distance_traveled=user.distance_traveled
    )
    db.session.add(history)

    user.name = data.get('name', user.name)
    user.age = data.get('age', user.age)
    user.weight = data.get('weight', user.weight)
    user.height = data.get('height', user.height)
    user.heart_rhythm = data.get('heart_rhythm', user.heart_rhythm)
    user.number_of_steps = data.get('number_of_steps', user.number_of_steps)
    user.distance_traveled = data.get('distance_traveled', user.distance_traveled)

    db.session.commit()
    return jsonify(user.as_dict()), 200

@app.route('/profiles/<int:user_id>', methods=['DELETE'])
def delete_profile(user_id):
    user = UserProfile.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return '', 204

@app.route('/profiles/<int:user_id>/history', methods=['GET'])
def get_profile_history(user_id):
    history = UserProfileHistory.query.filter_by(user_id=user_id).order_by(UserProfileHistory.timestamp.desc()).all()
    return jsonify([h.as_dict() for h in history])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
