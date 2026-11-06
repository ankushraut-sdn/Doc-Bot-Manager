# Doc-Bot-Manager

## 1. Project Overview

A multi-tenant document chatbot platform. Users authenticate, create "bots," upload documents (PDF/TXT) to each bot, and the backend builds a FAISS vector index per bot so the bot can answer questions grounded in its own documents. Bots can also be embedded on external pages via a token-protected widget.

## 2. Core Features

- JWT-based user authentication (`app/api/auth.py`)
- Create/list chatbots per user, each with its own document set and vector index (`app/api/bots.py`)
- Document upload and ingestion into a FAISS index with sentence-transformer embeddings (`app/api/documents.py`, `app/services/document.py`, `app/services/embedding.py`)
- Chat endpoint that retrieves relevant document chunks and generates an answer via an LLM (`app/api/chat.py`, `app/services/llm.py`)
- Embeddable, token-authenticated chat widget served as a standalone HTML page
- SQLite database for user/bot metadata; per-bot FAISS indexes and extracted text metadata stored under `data/`

## 3. Tech Stack

| Component | Technology |
|---|---|
| Web framework | Flask, Flask-JWT-Extended, Flask-CORS, Flask-Migrate |
| Database | SQLAlchemy + SQLite |
| Vector search | FAISS (`faiss-cpu`) |
| Embeddings | `sentence-transformers` (default: `sentence-transformers/all-MiniLM-L6-v2`) |
| Document parsing | `pypdf` |
| Answer generation | OpenAI API |

## 4. Project Structure

```
Doc-Bot-Manager/
├── app/
│   ├── api/            # Flask blueprints: auth, bots, documents, chat, health/widget
│   ├── services/       # document parsing, embedding, LLM integration
│   ├── models.py        # SQLAlchemy models (User, Bot, ...)
│   ├── config.py        # paths, env-driven settings
│   └── extensions.py     # Flask extensions (db, jwt, cors)
├── data/
│   ├── uploads/          # raw uploaded documents, per bot
│   ├── indexes/           # FAISS index files, per bot
│   ├── meta/              # chunk/document metadata per bot
│   └── app.sqlite         # application database
├── run.py                 # entrypoint
└── requirements.txt
```

## 5. Prerequisites

- Python 3.10+
- An OpenAI API key for answer generation

## 6. How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables (create a `.env` file in the project root):
   ```env
   FLASK_SECRET=your-flask-secret
   JWT_SECRET=your-jwt-secret
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   OPENAI_API_KEY=your-openai-api-key
   PORT=5000
   ```
3. Run the app (creates the SQLite tables automatically on first start):
   ```bash
   python run.py
   ```
   The API is served at `http://localhost:5000`.

## 7. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register` | Register a new user; returns a JWT access token. |
| POST | `/api/login` | Authenticate an existing user; returns a JWT access token. |
| POST | `/api/bots` | Create a new bot for the authenticated user. |
| GET | `/api/bots` | List the authenticated user's bots. |
| POST | `/api/bots/<bot_id>/widget-token` | Issue a token for embedding the bot's chat widget externally. |
| POST | `/api/bots/<bot_id>/documents` | Upload a document (PDF/TXT) to a bot. |
| POST | `/api/bots/<bot_id>/embed` | Trigger embedding/indexing of a bot's uploaded documents. |
| POST | `/api/bots/<bot_id>/chat` | Ask a question; retrieves relevant chunks and returns an LLM-generated answer. |
| GET | `/api/health` | Health check. |
| GET | `/widget/<bot_id>` | Token-authenticated, embeddable chat widget page. |

## 8. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `FLASK_SECRET` | `"dev-secret"` | Flask session secret key. |
| `JWT_SECRET` | `"dev-jwt"` | JWT signing secret. |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence-transformers model used for document embeddings. |
| `OPENAI_API_KEY` | — | Required for chat answer generation. |
| `PORT` | `5000` | Port the Flask app listens on. |

## 9. Known Limitations

- Default `FLASK_SECRET`/`JWT_SECRET` values are development placeholders and must be overridden before any shared or production use.
- No automated tests currently exist in the repository (`test_suite_analysis/` contains only a metadata stub, not test code).

## License

No LICENSE file is present in this repository.
