# Import Python Regular Expression Package
import re
# Import Flask Package
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# Import Operating System Package
import os
# Import OpenAI API
import openai
# Import Dotenv Package
from dotenv import load_dotenv
# Import SQLAlchemy Package
from flask_sqlalchemy import SQLAlchemy
# Import Flask Login Package
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Import Argon2 Package
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Password Hashing
ph = PasswordHasher()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize SQLAlchemy Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config = os.getenv ("SECRET_KEY")
db = SQLAlchemy(app)

# User Model With Signup Form Fields
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Application Routing

# Home Page
@app.route('/')
def index():
    return render_template('landing.html')

# Application for Authenticated Users
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

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
                    return redirect(url_for('dashboard'))
            except VerifyMismatchError:
                pass
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Logout Route
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

# Prompt Generation

objections = {
    "We're using your competitor": "And how are you finding them? If you don’t mind me asking, why did you choose to go with them?",
    "Your product is too expensive": "Cost is an important consideration but I believe we can actually save you money. Can we set up a time for me to explain how?",
    "I don't see any ROI potential": "There’s definitely potential. I’d love to show you and explain how. Are you available this week for a more detailed call?",
}

# Chatbot Functionality

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('user_input')

    if len(user_input) > 140: # Limit Objection Input to 140 Characters
        return jsonify({"error": "Objection is too long. Please limit your objection to 140 characters, or less."})

# Prompt Generation
    prompt = f"A prospective client mentioned, \"{user_input}\" How would you address this concern?\n\nSales Sensei:"
    response = openai.Completion.create(
        model="davinci:ft-personal-2023-04-17-22-02-12", # Model ID
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

# Database Creation
with app.app_context():
    db.create_all()

# Run Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))