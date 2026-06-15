from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize directories
    config_class.init_directories()

    # Initialize extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)

    return app
