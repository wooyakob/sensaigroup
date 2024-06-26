from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db
from argon2 import PasswordHasher

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    is_admin = db.Column(db.Boolean, default = False)

    def set_password(self, password):
        password_hasher = PasswordHasher()
        self.password = password_hasher.hash(password)

    def check_password(self, password):
        password_hasher = PasswordHasher()
        try:
            password_hasher.verify(self.password, password)
            return True
        except:
            return False

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(100))
    objection = db.Column(db.Text, nullable=True)
    product_selected = db.Column(db.String(200), nullable=True) 
    product_objection = db.Column(db.Text, nullable=True)
    product_advice = db.Column(db.Text, nullable=True)
    ai_response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.relationship('User', backref='interactions')

    def to_dict(self):
        return {
            'objection': self.objection,
            'product_objection': self.product_objection,
            'product_advice': self.product_advice,
            'ai_response': self.ai_response,
            'rating': self.rating,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
            'id': self.id
        }
    
class LoginActivity(db.Model):
    __tablename__ = "login_activity"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    username = db.Column(db.String(100))
    login_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S'),
            'id': self.id
        }

class Product(db.Model):
    __tablename__ = "products"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='products')
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), unique=False, nullable=False)
    product_info = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'product_name': self.product_name,
            'product_info': self.product_info,
            'id': self.id
        }