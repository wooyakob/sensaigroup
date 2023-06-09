import logging
from datetime import datetime
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from itsdangerous import URLSafeTimedSerializer
import os
import openai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
ph = PasswordHasher()
openai.api_key = os.getenv("OPENAI_API_KEY")
app.config["MAIL_SERVER"] = "smtp.mail.me.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "jake_wood@mac.com"
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = "jake_wood@mac.com"
app.config['EMAIL_SECRET_KEY'] = os.getenv("EMAIL_SECRET_KEY")
mail = Mail(app)
@app.route("/forgot_username", methods=["GET", "POST"])
def forgot_username():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            send_username_email(user)
            flash("An email with your username has been sent to your email address.")
        else:
            flash("No account found with that email address.")
        return redirect(url_for("login"))

    return render_template("forgot_username.html")
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            flash("An email with password reset instructions has been sent to your email address.")
            return redirect(url_for("login"))
        else:
            flash("No account found with that email address.")
    return render_template("forgot_password.html")
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        if new_password != confirm_password:
            flash("New password and confirm password do not match.")
            return redirect(url_for("reset_password", token=token))
        email = token_to_email(token)
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("Invalid or expired token.")
            return redirect(url_for("forgot_password"))
        hashed_password = ph.hash(new_password)
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been successfully reset. Please log in with your new password.")
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)
def generate_password_reset_token(user):
    serializer = URLSafeTimedSerializer(app.config["EMAIL_SECRET_KEY"])
    return serializer.dumps(user.email, salt="password-reset")
def send_username_email(user):
    msg = Message("Your Sales Sensei Username", recipients=[user.email])
    msg.body = f"Your Sales Sensei username is: {user.username}"
    mail.send(msg)
def send_password_reset_email(user):
    token = generate_password_reset_token(user)
    reset_url = url_for("reset_password", token=token, _external=True)
    msg = Message("Sales Sensei Password Reset", recipients=[user.email])
    msg.body = f"To reset your password, please click the following link: {reset_url}"
    mail.send(msg)
def token_to_email(token):
    serializer = URLSafeTimedSerializer(app.config["EMAIL_SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
        return email
    except:
        return None
def is_valid_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.match(regex, email)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(120))
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    objection = db.Column(db.Text, nullable=False)
    suggested_response = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.relationship('User', backref='interactions') 
admin = Admin(app, name='My App Admin', template_mode='bootstrap3')
class InteractionModelView(ModelView):
    column_list = ('id', 'user', 'objection', 'suggested_response', 'ai_response', 'rating', 'timestamp')
    column_labels = {
        'user': 'User',
        'objection': 'Objection',
        'suggested_response': 'Suggested Response',
        'ai_response': 'AI Response',
        'rating': 'Rating',
        'timestamp': 'Timestamp'
    }
    column_searchable_list = ['user.first_name', 'user.last_name', 'user.email', 'user.username']
    def _user_formatter(view, context, model, name):
        if model.user:
            return model.user.username
        return ""
    
    column_formatters = {
        'user': _user_formatter,
    }
admin.add_view(ModelView(User, db.session))
admin.add_view(InteractionModelView(Interaction, db.session))
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        company = request.form['company']
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not email or not password or not username:
            flash('Email, username, and password cannot be empty.', 'danger')
            return render_template('signup.html')
        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('signup.html')
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Email or username already exists. Please choose a different one.', 'danger')
            return render_template('signup.html')
        hashed_password = ph.hash(password)
        user = User(
            first_name=first_name,
            last_name=last_name,
            company=company,
            email=email,
            username=username,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("You have successfully signed up to use Sales Sensei! Please log in to begin handling your objections.", 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def index():
    return render_template('landing.html')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            try:
                if ph.verify(user.password, password):
                    login_user(user)
                    return redirect(url_for('dashboard'))
            except VerifyMismatchError:
                pass
        flash('Invalid username or password.', 'danger') 
    return render_template('login.html')
@app.route('/blog')
def blog():
    return render_template('blog.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/rate', methods=['POST'])
def rate():
    rating = request.json.get('rating')
    return jsonify({"message": "Rating received"})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"})
    
    user_objection = request.json.get('user_objection')
    user_response = request.json.get('user_response')

    if len(user_objection) > 140: 
        return jsonify({"error": "Objection is too long. Please limit your objection to 140 characters or less."})
    
    messages = [
        {"role": "system", "content": 
        "You are stepping into the shoes of a top-tier sales expert, specifically tuned to hone in on relationship-building with the end goal of securing a sale. As this seasoned professional, you are called upon by other sales representatives seeking your advice on overcoming objections and challenges raised by potential customers – obstacles that hinder a sale.\n\n" 
        "Your job is to provide these sales representatives with strategic advice tailored to each unique objection, considering both product and company context to ensure highly relevant and accurate guidance. Your advice should be concise, spanning no more than three paragraphs.\n\n" 
        "Your conversation's primary objective is to train the representatives, leading them to an effective strategy for addressing the initial objection. By probing the representatives with insightful questions, you help them develop solutions and build their skills.\n\n" 
        "The ultimate goal is to shape them into top performers, enhancing their abilities to professionally and skillfully respond to customer objections, queries, and challenges. A significant aspect of your guidance involves recognizing the stage in the sales lifecycle where the objection occurred and customizing your advice accordingly.\n\n"
        "You rely on the best sales strategies, applying them to specific scenarios presented to you.\n\n"
        "You provide responses in no more than three paragraphs and clearly separate out your points with paragraphs.\n\n"
    },
        {"role": "user", "content": user_objection},
        {"role": "assistant", "content": user_response}
]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
    )
    
    response_text = response.choices[0].message.content.strip()
    
    interaction = Interaction(
        user_id=current_user.id,
        objection=user_objection,
        suggested_response=user_response,
        ai_response=response_text
    )
    db.session.add(interaction)
    db.session.commit()

    return jsonify({"response_text": response_text, "interaction_id": interaction.id})

with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))