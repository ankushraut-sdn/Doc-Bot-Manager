import datetime as dt
from app.extensions import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    bots = db.relationship("Bot", backref="owner", lazy=True)

    def to_dict(self):
        return {"id": self.id, "email": self.email}


class Bot(db.Model):
    __tablename__ = 'bot'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    iframe_token = db.Column(db.String(255), unique=True, nullable=True)

    documents = db.relationship("Document", backref="bot", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "slug": self.slug,
            "created_at": self.created_at.isoformat(),
            "iframe_token": self.iframe_token,
        }


class Document(db.Model):
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey("bot.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    size_bytes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "bot_id": self.bot_id,
            "filename": self.filename,
            "original_name": self.original_name,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
        }
