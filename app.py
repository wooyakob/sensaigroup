#imports
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import openai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_session import Session



load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session/'
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

#classes for info that's stored in SQL database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/landing')
def landing():
    return render_template('landing.html')

# Authentication Route, if authenticated display index, if not display landing
@app.route('/')
def index():
    if current_user.is_authenticated:
        session['unlimited'] = current_user.is_authenticated
        return render_template('index.html')
    else:
        return redirect(url_for('landing'))

#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

#Logout Route
@app.route('/logout')
@login_required
def logout():
    session.pop('questions_asked', None)
    logout_user()
    return redirect(url_for('index'))

#Return Home
@app.route('/landing')
def home():
    return render_template('landing.html')

#Signup Route

def is_valid_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.match(regex, email)

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

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose a different one.', 'danger')
            return render_template('signup.html')

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

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

objections = {
    "We're using your competitor": "And how are you finding them? If you don’t mind me asking, why did you choose to go with them?",
    "Your product is too expensive": "Cost is an important consideration but I believe we can actually save you money. Can we set up a time for me to explain how?",
    "I don't see any ROI potential": "There’s definitely potential. I’d love to show you and explain how. Are you available this week for a more detailed call?",
}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    questions_asked = session.get('questions_asked', 0)
    unlimited = session.get('unlimited', False)
    user_input = request.json.get('user_input')
    prompt = f"A prospective client mentioned, \"{user_input}\" How would you address this concern?\n\nSales Sensei:"
    response = openai.Completion.create(
        model="davinci:ft-personal-2023-04-17-22-02-12",
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=2,
        stop=["END", "A prospective client mentioned"]
    )
    response_text = response.choices[0].text.strip()
    response_text = re.search(r'(.*[.!?])', response_text).group(0)
    return jsonify(response_text)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(500), nullable=False)
    ai_response = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('feedback', lazy=True))

@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    user_input = request.form['user_input']
    ai_response = request.form['ai_response']
    rating = request.form['rating']

    feedback_entry = Feedback(user_input=user_input, ai_response=ai_response, rating=rating, user=current_user)
    db.session.add(feedback_entry)
    db.session.commit()

    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)