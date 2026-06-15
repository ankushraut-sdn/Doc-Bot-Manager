import os
import io
import json
from typing import List, Tuple, Dict, Any
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer
from app.config import Config
from app.models import Bot, Document
from app.services.document import extract_text_from_pdf, clean_text, chunk_text

# Lazy-load the embedding model once per process
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    """Lazy loads and returns the SentenceTransformer model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(Config.DEFAULT_MODEL_NAME)
    return _embedding_model

def bot_dir(bot_id: int) -> str:
    """Get or create the directory path where a bot's documents are uploaded."""
    d = os.path.join(Config.UPLOAD_DIR, str(bot_id))
    os.makedirs(d, exist_ok=True)
    return d

def bot_index_paths(bot_id: int) -> Tuple[str, str]:
    """Get the path to the FAISS index file and its metadata JSON file for a bot."""
    idx_path = os.path.join(Config.INDEX_DIR, f"bot_{bot_id}.faiss")
    meta_path = os.path.join(Config.META_DIR, f"bot_{bot_id}_meta.json")
    return idx_path, meta_path

def load_or_create_index(bot_id: int, dim: int) -> faiss.IndexFlatIP:
    """Load an existing FAISS index for a bot or create a new flat inner-product index."""
    idx_path, _ = bot_index_paths(bot_id)
    if os.path.exists(idx_path):
        index = faiss.read_index(idx_path)
        return index  # type: ignore
    return faiss.IndexFlatIP(dim)  # cosine similarity via normalized vectors

def save_index_and_meta(bot_id: int, index: faiss.IndexFlatIP, chunks: List[str], sources: List[Dict[str, Any]]):
    """Save the FAISS index file and corresponding metadata (chunks & sources) to disk."""
    idx_path, meta_path = bot_index_paths(bot_id)
    faiss.write_index(index, idx_path)
    meta = {"chunks": chunks, "sources": sources}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

def load_meta(bot_id: int) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Load metadata (chunks & sources) for a bot from disk."""
    _, meta_path = bot_index_paths(bot_id)
    if not os.path.exists(meta_path):
        return [], []
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return meta.get("chunks", []), meta.get("sources", [])

def embed_texts(texts: List[str]):
    """Generate normalized embeddings for a list of texts using SentenceTransformers."""
    model = get_embedding_model()
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return emb

def build_embeddings_for_bot(bot_id: int) -> int:
    """Build or rebuild the embedding index and metadata for all documents under a given bot."""
    bot = Bot.query.filter_by(id=bot_id).first()
    if not bot:
        raise ValueError("bot not found")

    docs = Document.query.filter_by(bot_id=bot.id).all()
    if not docs:
        raise ValueError("no documents to embed")

    texts: List[str] = []
    sources: List[Dict[str, Any]] = []

    for d in docs:
        path = os.path.join(bot_dir(bot.id), d.filename)
        ext = d.filename.rsplit(".", 1)[-1].lower()
        try:
            if ext == "txt":
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    raw = fp.read()
            elif ext == "pdf":
                with open(path, "rb") as fp:
                    raw = extract_text_from_pdf(io.BytesIO(fp.read()))
            else:
                # skip unsupported types
                continue
        except Exception:
            # skip unreadable docs
            continue

        raw = clean_text(raw)
        chunks = chunk_text(raw)
        for ch in chunks:
            texts.append(ch)
            sources.append({"document_id": d.id, "filename": d.original_name})

    if not texts:
        raise ValueError("no text extracted from documents")

    embeddings = embed_texts(texts)  # -> np.ndarray [N, dim]
    dim = int(embeddings.shape[1])

    # Rebuild a fresh index for idempotency
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    save_index_and_meta(bot.id, index, texts, sources)
    return int(index.ntotal)
