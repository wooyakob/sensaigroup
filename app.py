from models import User, Interaction, LoginActivity, Product
from extensions import db, init_app
from admin import admin
from admin import init_admin
import pandas as pd
import logging
from datetime import datetime
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from itsdangerous import URLSafeTimedSerializer
import os
from openai.error import OpenAIError
import openai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask_migrate import Migrate
from products import products

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(products)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

    migrate = Migrate(app, db)
    init_app(app)
    init_admin(app)

    return app

app = create_app()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


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


def get_product_context(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return None

    product_info = f"""
    You are currently discussing the product named {product.product_name}. 
    Product Info: {product.product_info}. 
    Design Rationale: {product.design_rationale}.
    """
    
    return product_info


@app.route('/admin/createuser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([first_name, last_name, email, username, password]):
            return render_template('createuser.html', error_message='Missing required fields')

        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, is_admin=False)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('createuser.html')

@app.route('/rate_interaction', methods=['POST'])
@login_required
def rate_interaction():
    data = request.get_json()
    rating = data.get('rating', None)
    if rating is None:
        return jsonify({'message': 'Bad Request: No rating provided'}), 400

    last_interaction = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.timestamp.desc()).first()
    
    if last_interaction is None:
        return jsonify({'message': 'No interaction found'}), 404

    last_interaction.rating = rating
    db.session.commit()

    return jsonify({'message': 'Rating saved successfully'}), 200

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

@app.route('/download_history', methods=['GET'])
@login_required
def download_history():
    user_interactions = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.timestamp.desc()).all()

    interactions_dict = [interaction.to_dict() for interaction in user_interactions]

    df = pd.DataFrame(interactions_dict)

    filename = f"{current_user.username}_history.xlsx"
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)

@app.route('/download_login_report', methods=['GET'])
@login_required
def download_login_report():
    user_logins = LoginActivity.query.order_by(LoginActivity.login_time.desc()).all()

    logins_dict = [{'username': login.username, 'login_time': login.login_time} for login in user_logins]

    df = pd.DataFrame(logins_dict)

    filename = "login_report.xlsx"
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)

@app.route('/download_user_activity_report', methods=['GET'])
@login_required
def download_user_activity_report():
    user_interactions = Interaction.query.order_by(Interaction.timestamp.desc()).all()

    interactions_dict = [{'username': interaction.username, 'objection': interaction.objection, 'ai_response': interaction.ai_response, 'rating': interaction.rating, 'timestamp': interaction.timestamp} for interaction in user_interactions]

    df = pd.DataFrame(interactions_dict)

    filename = "user_activity_report.xlsx"
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)

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
        if not is_strong_password(new_password):
            flash("Password should include upper and lowercase letters, digits, symbols, and at least 15 characters.")
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
    msg = Message("Your Sales SensAI Username", recipients=[user.email])
    msg.body = f"Your Sales SensAI username is: {user.username}"
    mail.send(msg)

def send_password_reset_email(user):
    token = generate_password_reset_token(user)
    reset_url = url_for("reset_password", token=token, _external=True)
    msg = Message("Sales SensAI Password Reset", recipients=[user.email])
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/admin/reports', methods=['GET'])
def reports():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin not authenticated"})
    else:
        return render_template('reports.html')

@app.route('/admin/products', methods=['GET'])
def products():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin not authenticated"})
    else:
        return render_template('products.html')

@app.route('/admin/reports/logins', methods=['GET'])
def report_logins():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin not authenticated"})
    
    logins = LoginActivity.query.all()
    
    return render_template('login_report.html', logins=logins)

@app.route('/admin/reports/user_activity', methods=['GET'])
def report_user_activity():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin not authenticated"})
    
    interactions = Interaction.query.all()
    
    return render_template('user_activity_report.html', interactions=interactions)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user:
            try:
                if ph.verify(user.password, password):
                    login_user(user)
                    return redirect(url_for('admin_dashboard'))
            except VerifyMismatchError:
                pass
        flash('Invalid username or password.', 'danger')
    return render_template('admin_login.html')

@app.route('/user_history', methods=['GET'])
@login_required
def user_history():
    objections = Interaction.query.filter_by(user_id=current_user.id, product_objection=None, product_advice=None).order_by(Interaction.timestamp.desc()).all()
    product_objections = Interaction.query.filter_by(user_id=current_user.id, objection=None, product_advice=None).order_by(Interaction.timestamp.desc()).all()
    product_questions = Interaction.query.filter_by(user_id=current_user.id, objection=None, product_objection=None).order_by(Interaction.timestamp.desc()).all()

    for interaction in objections + product_objections + product_questions:
        product = Product.query.filter_by(id=interaction.product_selected).first()
        if product:
            interaction.product_selected = product.product_name

    return render_template('user_history.html', objections=objections, product_objections=product_objections, product_questions=product_questions)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.all()
    return render_template('index.html', products=products) 

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
                    login_activity = LoginActivity(user_id=user.id, username=user.username)
                    db.session.add(login_activity)
                    db.session.commit()
                    return redirect(url_for('dashboard'))
            except VerifyMismatchError:
                pass
        flash('Invalid username or password.', 'danger') 
    return render_template('login.html')

@app.route('/admin_dash')
@login_required
def admin_dashboard():
    return render_template('admin_dash.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

#INTERACTION ENDPOINTS. GENERIC OBJECTIONS

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"})

    user_objection = request.json.get('user_objection')

    messages = [
        {"role": "system", "content":
            """You will respond in plain English. You will respond in an informal conversational manner. You will be polite, friendly, and professional but not too formal or corporate.\n\n"
            "You value conciseness and brevity. Your responses will be short and to the point. You will not use long, complex sentences.\n\n"
            "You are a medical device sales expert and top performing sales representative. You understand how to handle customer objections professionally.\n\n"
            "You address the specific objection entered and deal with it in a structured and logical way. You handle the objection as if you were selling the medical device yourself.\n\n"""                           
        },
        {"role": "user", "content": user_objection},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
        )
    except openai.error.ServiceUnavailableError:
        return jsonify({"error": "AI service is currently unavailable. Please try again later."})

    response_text = response.choices[0].message.content.strip()
    response_text = response_text.replace('\n', '<br>')
    response_text = '<p>' + '</p><p>'.join(response_text.split('\n\n')) + '</p>'

    try:
        interaction = Interaction(
            user_id=current_user.id,
            username=current_user.username,
            objection=user_objection,
            ai_response=response_text,
            product_selected=None 
        )
        db.session.add(interaction)
        db.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

    return jsonify({"response_text": response_text, "interaction_id": interaction.id, "regenerate": True})

#INTERACTION ENDPOINTS. PRODUCT OBJECTIONS

@app.route('/product_objection_advice', methods=['POST'])
def product_objection_advice():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"})

    message = request.json.get('message')
    product_id = request.json.get('product_id')

    product_context = get_product_context(product_id)
    if product_context is None:
        return jsonify({'error': 'Invalid product ID'})

    instructions = """You will respond in plain English. You will respond in an informal conversational manner. You will be polite, friendly, and professional but not too formal or corporate.\n\n"
        "You value conciseness and brevity. Your responses will be short and to the point. You will not use long, complex sentences.\n\n"
        "You are a medical device sales expert and top performing sales representative. You understand how to handle customer objections professionally.\n\n"
        "You address the specific objection entered and deal with it in a structured and logical way. You handle the objection as if you were selling the product yourself."""

    messages = [
        {"role": "system", "content": instructions + "\n\n" + product_context},
        {"role": "user", "content": message},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
        )
    except openai.error.ServiceUnavailableError:
        return jsonify({"error": "AI service is currently unavailable. Please try again later."})

    response_text = response.choices[0].message.content.strip()
    response_text = response_text.replace('\n', '<br>')
    response_text = '<p>' + '</p><p>'.join(response_text.split('\n\n')) + '</p>'

    try:
        interaction = Interaction(
            user_id=current_user.id,
            username=current_user.username,
            product_objection=message,
            ai_response=response_text,
            product_selected=product_id
    )
        db.session.add(interaction)
        db.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

    return jsonify({"response_text": response_text, "regenerate": True})


#INTERACTION ENDPOINTS. PRODUCT ADVICE

@app.route('/product_advice', methods=['POST'])
def product_advice():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"})
    
    message = request.json.get('message')
    product_id = request.json.get('product_id')

    product_context = get_product_context(product_id)
    if product_context is None:
        return jsonify({'error': 'Invalid product ID'})

    instructions = """You are a knowledgeable sales representative for the products in question. Answer the user's question about the product accurately and succinctly, using the provided product context when relevant."""

    messages = [
        {"role": "system", "content": instructions + "\n\n" + product_context},
        {"role": "user", "content": message},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
        )
    except openai.error.ServiceUnavailableError:
        return jsonify({"error": "AI service is currently unavailable. Please try again later."})

    response_text = response.choices[0].message.content.strip()
    response_text = response_text.replace('\n', '<br>')
    response_text = '<p>' + '</p><p>'.join(response_text.split('\n\n')) + '</p>'

    try:
        interaction = Interaction(
            user_id=current_user.id,
            username=current_user.username,
            product_advice=message, 
            ai_response=response_text,
            product_selected=product_id 
        )
        db.session.add(interaction)
        db.session.commit()
    except SQLAlchemyError as e:
       return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

    return jsonify({"response_text": response_text, "regenerate": True})

if __name__ == "__main__":
    with app.app_context():
        create_admin() 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))