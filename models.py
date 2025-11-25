from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    generations = db.relationship(
        "Generation", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Generation(db.Model):
    __tablename__ = "generations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    draft_link = db.Column(db.String(500), nullable=True)
    generation_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship(
        "GeneratedImage", backref="generation", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Generation {self.generation_id}>"


class GeneratedImage(db.Model):
    __tablename__ = "generated_images"

    id = db.Column(db.Integer, primary_key=True)
    generation_id = db.Column(
        db.String(36), db.ForeignKey("generations.generation_id"), nullable=False
    )
    image_data = db.Column(db.LargeBinary, nullable=False)
    index_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GeneratedImage {self.generation_id}[{self.index_number}]>"
