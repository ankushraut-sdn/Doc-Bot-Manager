import hashlib
from flask_jwt_extended import get_jwt_identity

def hash_password(pw: str) -> str:
    """Hash a plaintext password using SHA-256."""
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def check_password(pw: str, h: str) -> bool:
    """Verify a password against a SHA-256 hash."""
    return hash_password(pw) == h

def current_user_id() -> int:
    """Retrieve the current user ID from the active JWT token."""
    identity = get_jwt_identity()
    return int(identity)
