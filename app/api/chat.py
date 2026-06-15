import os
from typing import List, Tuple, Dict, Any
import faiss  # type: ignore
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Bot
from app.api.utils import current_user_id
from app.services.embedding import bot_index_paths, load_meta, embed_texts
from app.services.llm import openai_answer

chat_bp = Blueprint("chat", __name__)

def retrieve(bot_id: int, query: str, k: int = 5) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
    """Retrieve top k nearest neighbor chunks from FAISS vector DB for a given query."""
    idx_path, _ = bot_index_paths(bot_id)
    chunks, sources = load_meta(bot_id)
    if not os.path.exists(idx_path) or not chunks:
        return [], [], []

    index = faiss.read_index(idx_path)
    q_emb = embed_texts([query])
    D, I = index.search(q_emb, k)
    
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []
    scores: List[float] = []
    for score, idx in zip(D[0].tolist(), I[0].tolist()):
        if 0 <= idx < len(chunks):
            docs.append(chunks[idx])
            metas.append(sources[idx])
            scores.append(float(score))
    return docs, metas, scores

@chat_bp.post("/bots/<int:bot_id>/chat")
@jwt_required(optional=True)
def chat(bot_id: int):
    """Retrieve relevant context and generate chatbot response to the user's question."""
    identity = get_jwt_identity()

    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    # If the user is authenticated, ensure they own the bot.
    if identity:
        user_id = current_user_id()
        bot = Bot.query.filter_by(id=bot_id, user_id=user_id).first()
        if not bot:
            return jsonify({"error": "bot not found"}), 404
    else:
        # Unauthenticated path: require valid iframe token (e.g. from widgets)
        token = request.headers.get("X-Widget-Token") or request.args.get("token")
        bot = Bot.query.filter_by(id=bot_id, iframe_token=token).first() if token else None
        if not bot:
            return jsonify({"error": "unauthorized"}), 401

    docs, metas, scores = retrieve(bot.id, question, k=5)
    if not docs:
        return jsonify({"answer": "No knowledge base found for this bot yet.", "contexts": []})

    context = "\n---\n".join(docs)
    answer = openai_answer(question, context)
    print("this is the answer================>", answer)

    return jsonify({
        "answer": answer,
        "contexts": [{"text": t, "meta": m, "score": s} for t, m, s in zip(docs, metas, scores)],
    })
