import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Bot
from app.api.utils import current_user_id

bots_bp = Blueprint("bots", __name__)

@bots_bp.post("/bots")
@jwt_required()
def create_bot():
    """Create a new chatbot instance for the authenticated user."""
    user_id = current_user_id()
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    
    if not name:
        return jsonify({"error": "name required"}), 400

    slug_base = "-".join(name.lower().split()) or f"bot-{uuid.uuid4().hex[:6]}"
    slug = slug_base
    i = 1
    while Bot.query.filter_by(slug=slug).first() is not None:
        slug = f"{slug_base}-{i}"
        i += 1

    b = Bot(user_id=user_id, name=name, slug=slug)
    db.session.add(b)
    db.session.commit()
    return jsonify({"bot": b.to_dict()})

@bots_bp.get("/bots")
@jwt_required()
def list_bots():
    """List all chatbot instances owned by the authenticated user."""
    user_id = current_user_id()
    bots = Bot.query.filter_by(user_id=user_id).order_by(Bot.created_at.desc()).all()
    return jsonify({"bots": [b.to_dict() for b in bots]})

@bots_bp.post("/bots/<int:bot_id>/widget-token")
@jwt_required()
def create_widget_token(bot_id: int):
    """Generate a unique iframe widget token for a chatbot to allow public embedding."""
    user_id = current_user_id()
    bot = Bot.query.filter_by(id=bot_id, user_id=user_id).first()
    if not bot:
        return jsonify({"error": "bot not found"}), 404
        
    bot.iframe_token = uuid.uuid4().hex
    db.session.commit()
    return jsonify({
        "bot": bot.to_dict(), 
        "widget_url": f"/widget/{bot.id}?token={bot.iframe_token}"
    })
