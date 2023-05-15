# Import Logging Package
import logging

# Import Python Regular Expression Package
import re
# Import Flask Package
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

# Email Package: Generate secure tokens that can be used for tasks like password resets, email confirmation links
from itsdangerous import URLSafeTimedSerializer

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

# Import Flask SMTP Email Package (Simple Mail Transfer Protocol is a TCP/IP protocol used in sending and receiving email)
from flask_mail import Mail, Message

# Import Argon2 Package
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Configure Logging Settings
logging.basicConfig(level=logging.DEBUG)

# Password Hashing
ph = PasswordHasher()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email configuration
# Apple ICloud Settings
app.config["MAIL_SERVER"] = "smtp.mail.me.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "jake_wood@mac.com"
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = "jake_wood@mac.com"
app.config['EMAIL_SECRET_KEY'] = os.getenv("EMAIL_SECRET_KEY")

mail = Mail(app)

# Email Routes
# Forgot Email
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
        return redirect(url_for("login"))  # Redirect to the login page

    return render_template("forgot_username.html")

# Forgot Password
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            flash("An email with password reset instructions has been sent to your email address.")
            return redirect(url_for("login"))  # Redirect to the login page after sending the reset email
        else:
            flash("No account found with that email address.")
    
    return render_template("forgot_password.html")

# Reset Password
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Validate new password and confirm password
        if new_password != confirm_password:
            flash("New password and confirm password do not match.")
            return redirect(url_for("reset_password", token=token))

        # Retrieve user based on token
        email = token_to_email(token)
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("Invalid or expired token.")
            return redirect(url_for("forgot_password"))

        # Update password
        hashed_password = ph.hash(new_password)
        user.password = hashed_password
        db.session.commit()

        flash("Your password has been successfully reset. Please log in with your new password.")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)

# Password and Email Reset Token Generation Function
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


# define token to email function
def token_to_email(token):
    serializer = URLSafeTimedSerializer(app.config["EMAIL_SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)  # Token expiration time: 1 hour
        return email
    except:
        return None


# Define Valid Email

def is_valid_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.match(regex, email)

# Database Configuration

# Initialize SQLAlchemy Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)

# User Model With Signup Form Fields
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Signup Route
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

        # Add success message after successful sign-up
        flash("You have successfully signed up to use Sales Sensei! Please log in to begin handling your objections.")

        return redirect(url_for('dashboard'))
    return render_template('signup.html')

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

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

#Email Validation
def is_valid_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.match(regex, email)

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