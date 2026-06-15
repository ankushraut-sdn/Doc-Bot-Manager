import os
from app import create_app
from app.extensions import db

app = create_app()

if __name__ == "__main__":
    # Create DB tables automatically on startup if they do not exist
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
