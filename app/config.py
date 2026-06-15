import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # Resolve BASE_DIR relative to the project root (config.py is in app/)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
    INDEX_DIR = os.path.join(DATA_DIR, "indexes")
    META_DIR = os.path.join(DATA_DIR, "meta")
    DB_PATH = os.path.join(DATA_DIR, "app.sqlite")

    # Ensure required data directories exist
    @classmethod
    def init_directories(cls):
        for d in (cls.DATA_DIR, cls.UPLOAD_DIR, cls.INDEX_DIR, cls.META_DIR):
            os.makedirs(d, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("FLASK_SECRET", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET", "dev-jwt")
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB upload cap

    DEFAULT_MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    ALLOWED_EXTENSIONS = {"txt", "pdf"}
