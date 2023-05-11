# Import necessary libraries
# Python Regular Expression Library
import re

# Import Flask libraries and components
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Import other required libraries
import os
import openai

# Import environment variable loader
from dotenv import load_dotenv
# Import SQLAlchemy for database management
from flask_sqlalchemy import SQLAlchemy
# Import Flask-Login for user authentication
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# Import Flask-Session for session management
from flask_session import Session
# Import Argon2 for password hashing
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
ph = PasswordHasher()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session/'
Session(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

# Define User model for the database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define user_loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Landing page route
@app.route('/landing')
def landing():
    return render_template('landing.html')

# Index route with authentication
@app.route('/')
def index():
    if current_user.is_authenticated:
        session['unlimited'] = current_user.is_authenticated
        return render_template('index.html')
    else:
        return redirect(url_for('landing'))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('login.html')
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                if ph.verify(user.password, password):
                    login_user(user)
                    return redirect(url_for('index'))
            except VerifyMismatchError:
                pass
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

#Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#Return Home
@app.route('/landing')
def home():
    return render_template('landing.html')

#Email Validation
def is_valid_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.match(regex, email)

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not email or not password:
            flash('Email and password cannot be empty.', 'danger')
            return render_template('signup.html')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('signup.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose a different one.', 'danger')
            return render_template('signup.html')

        hashed_password = ph.hash(password)
        user = User(email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

# Add headers to response to prevent caching
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.proxy_revalidate = True
    response.expires = 0
    response.pragma = 'no-cache'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Expires'] = '-1'
    return response

# Define objection dictionary
objections = {
    "We're using your competitor": "And how are you finding them? If you don’t mind me asking, why did you choose to go with them?",
    "Your product is too expensive": "Cost is an important consideration but I believe we can actually save you money. Can we set up a time for me to explain how?",
    "I don't see any ROI potential": "There’s definitely potential. I’d love to show you and explain how. Are you available this week for a more detailed call?",
}

# Chatbot route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    questions_asked = session.get('questions_asked', 0)
    unlimited = session.get('unlimited', False)
    user_input = request.json.get('user_input')

# Restrict objection token length
    if len(user_input) > 140:
        return jsonify("Objection is too long. Please limit your objection to 140 characters, or less.")

# Prompt engineering
    prompt = f"A prospective client mentioned, \"{user_input}\" How would you address this concern?\n\nSales Sensei:"
    response = openai.Completion.create(
        model="davinci:ft-personal-2023-04-17-22-02-12", # Unique training model ID
        prompt=prompt,
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=2,
        stop=["END",]
    )
    response_text = response.choices[0].text.strip()
    response_text = re.search(r'(.*[.!?])', response_text).group(0)
    return jsonify(response_text)

# Create database tables with app context
with app.app_context():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))