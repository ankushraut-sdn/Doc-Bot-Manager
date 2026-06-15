import os
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Bot, Document
from app.api.utils import current_user_id
from app.services.document import allowed_file
from app.services.embedding import bot_dir, build_embeddings_for_bot
from app.config import Config

documents_bp = Blueprint("documents", __name__)

@documents_bp.post("/bots/<int:bot_id>/documents")
@jwt_required()
def upload_document(bot_id: int):
    """Upload a text/pdf document for a chatbot and automatically update its vector embeddings."""
    user_id = current_user_id()
    bot = Bot.query.filter_by(id=bot_id, user_id=user_id).first()
    if not bot:
        return jsonify({"error": "bot not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
        
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400
        
    if not allowed_file(f.filename):
        return jsonify({"error": f"unsupported file type. Allowed: {sorted(Config.ALLOWED_EXTENSIONS)}"}), 400

    filename = secure_filename(f.filename)
    file_id = uuid.uuid4().hex
    stored_name = f"{file_id}_{filename}"
    path = os.path.join(bot_dir(bot.id), stored_name)
    f.save(path)

    size = os.path.getsize(path)
    doc = Document(bot_id=bot.id, filename=stored_name, original_name=filename, size_bytes=size)
    db.session.add(doc)
    db.session.commit()

    try:
        vector_count = build_embeddings_for_bot(bot.id)
        return jsonify({
            "document": doc.to_dict(),
            "embedding": {"status": "ok", "vectors": vector_count}
        }), 201
    except ValueError as ve:
        return jsonify({
            "document": doc.to_dict(),
            "embedding": {"status": "error", "message": str(ve)}
        }), 201
    except Exception as e:
        return jsonify({
            "document": doc.to_dict(),
            "embedding": {"status": "error", "message": "failed to build embeddings"}
        }), 201

@documents_bp.post("/bots/<int:bot_id>/embed")
@jwt_required()
def build_embeddings(bot_id: int):
    """Manually trigger embedding generation/re-indexing for all of a chatbot's uploaded documents."""
    user_id = current_user_id()
    bot = Bot.query.filter_by(id=bot_id, user_id=user_id).first()
    if not bot:
        return jsonify({"error": "bot not found"}), 404

    try:
        vector_count = build_embeddings_for_bot(bot.id)
        return jsonify({"status": "ok", "vectors": vector_count})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "failed to build embeddings"}), 500
