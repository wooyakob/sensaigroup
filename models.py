from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(120))
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    objection = db.Column(db.Text, nullable=False)
    suggested_response = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.relationship('User', backref='interactions')
