from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import User
from app.api.utils import hash_password, check_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    """Register a new user and return a JWT access token."""
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409
        
    u = User(email=email, password_hash=hash_password(password))
    db.session.add(u)
    db.session.commit()
    
    token = create_access_token(identity=str(u.id))
    return jsonify({"user": u.to_dict(), "token": token})

@auth_bp.post("/login")
def login():
    """Authenticate existing user and return a JWT access token."""
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    
    u = User.query.filter_by(email=email).first()
    if not u or not check_password(password, u.password_hash):
        return jsonify({"error": "invalid credentials"}), 401
        
    token = create_access_token(identity=str(u.id))
    return jsonify({"user": u.to_dict(), "token": token})
