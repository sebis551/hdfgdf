from flask import Flask
from .routes import user_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'

    app.register_blueprint(user_routes)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

