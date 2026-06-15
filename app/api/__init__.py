from flask import Blueprint
from app.api.auth import auth_bp
from app.api.bots import bots_bp
from app.api.documents import documents_bp
from app.api.chat import chat_bp
from app.api.main import main_bp

# Parent blueprint to mount all sub-blueprints cleanly
api_bp = Blueprint("api_parent", __name__)

# Register domain-specific blueprints under /api prefix
api_bp.register_blueprint(auth_bp, url_prefix="/api")
api_bp.register_blueprint(bots_bp, url_prefix="/api")
api_bp.register_blueprint(documents_bp, url_prefix="/api")
api_bp.register_blueprint(chat_bp, url_prefix="/api")

# Register main blueprint (handles root widget rendering and health check)
api_bp.register_blueprint(main_bp)
