# Import python regular expression module, which allows for pattern matching and text manipulation
import re
# Modules from the Flask web framework, which provides tools and utilities for building web applications in Python
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
# Operating system module, which provides a way to interact with the operating system
import os
# OpenAI API module, which provides a way to interact with the OpenAI API
import openai
# Module for loading environment variables from a .env file
from dotenv import load_dotenv
# Module for interacting with a Postgres database
from flask_sqlalchemy import SQLAlchemy
# Module for user authentication
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# Module for password hashing
from argon2 import PasswordHasher
# Module for password verification
from argon2.exceptions import VerifyMismatchError

# Load environment variables from .env file
load_dotenv()
# Create Flask app
app = Flask(__name__)
# Configure Flask app
ph = PasswordHasher()
# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
# Configure Postgres Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

#classes for info that's stored in SQL database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100), nullable=False)

# Configure Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication Route, if authenticated display index, if not display landing
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
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        company = request.form['company'].strip()

        if not all([email, password, first_name, last_name, company]):
            flash('All fields are required.', 'danger')
            return render_template('signup.html')

        ph = PasswordHasher()
        hashed_password = ph.hash(password)
        user = User(email=email, password=hashed_password, first_name=first_name, last_name=last_name, company=company)
        db.session.add(user)
        db.session.commit()

        flash('Thank you for signing up. Please log in to continue your Sales Sensei journey!')
        return redirect(url_for('login'))
    return render_template('signup.html')


# Objection Training
objections = {
    "We're using your competitor": "And how are you finding them? If you don’t mind me asking, why did you choose to go with them?",
    "Your product is too expensive": "Cost is an important consideration but I believe we can actually save you money. Can we set up a time for me to explain how?",
    "I don't see any ROI potential": "There’s definitely potential. I’d love to show you and explain how. Are you available this week for a more detailed call?",
}

# Chatbot Route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('user_input')

# Manage User Objection Input
    if len(user_input) > 140:
        return jsonify("Objection is too long. Please limit your objection to 140 characters, or less.")

# Prompt Engineering
    prompt = f"A prospective client mentioned, \"{user_input}\" How would you address this concern?\n\nSales Sensei:"
    response = openai.Completion.create(
        model="davinci:ft-personal-2023-04-17-22-02-12", # Fine Tuned Model
        prompt=prompt,
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=2,
        stop=["END",]
    )
    response_text = response.choices[0].text.strip() # Remove leading and trailing whitespace
    response_text = re.search(r'(.*[.!?])', response_text).group(0) # Remove trailing text after punctuation
    return jsonify(response_text) # Return response to user

with app.app_context(): # Create all tables in database
    db.create_all() # Create all tables in database

if __name__ == "__main__": # Run app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))