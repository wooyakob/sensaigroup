from models import User, Interaction, LoginActivity
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

load_dotenv()

def create_app():
    app = Flask(__name__)
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
    user_interactions = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.timestamp.desc()).all()
    return render_template('user_history.html', user_interactions=user_interactions)

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

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"})

    user_objection = request.json.get('user_objection')

    if len(user_objection) > 140:
        return jsonify({"error": "Objection is too long. Please limit your objection to 140 characters or less."})

    product_info = ""

    selected_product = request.json.get('selected_product')

    if selected_product == "Gorilla Universal Hevans Plate":
        product_info = (
            "The Gorilla® Universal HEvans® Plate is a product designed for use with the Evans Calcaneal Osteotomy. Here's a summary of the product features and benefits that a sales representative could use:\n\n"
            "1. Purpose: The Gorilla® HEvans® plate is specifically designed for use with the Evans Calcaneal Osteotomy.\n"
            "2. Design: The plate uses a 3 screw fixation construct to support the graft placed into the osteotomy. This design helps to prevent graft subsidence with subsequent loss of calcaneal length seen in the early post-operative period due to graft resorption.\n"
            "3. Placement: The design allows for a single proximal screw to be placed in the calcaneus with two distal screws placed in the anterior fragment of the calcaneus. Dual point fixation at the distal fragment mitigates the prospect of rotation of the distal fragment with the calcaneocuboid anatomy.\n"
            "4. Comfort: The posterior aspect of the plate is tapered to prevent peroneal tendon irritation in the location of the plate. The HEvans® plate is low profile (1.1 mm), with a tapering of the thickness to 0.5 mm toward the end to prevent soft tissue irritation.\n"
            "5. Rationale: Paragon 28® chose to design a 3 hole plate option for the Evans Calcaneal Osteotomy procedure to allow for less potential for soft tissue irritation at the posterior aspect, where interference with the peroneal tendons and/or sural nerve is a risk. The 3 hole HEvans® plate provides rotational stability for this procedure because of the large, flat calcaneocuboid joint. Because rotation about the proximal hole would require an arched path of the distal fragment, this is blocked by the calcaneocuboid joint.\n\n"
            "As a sales rep, you should emphasize the specific design features of the Gorilla® Universal HEvans® Plate that make it suitable for the Evans Calcaneal Osteotomy procedure, its low-profile design that minimizes soft tissue irritation, and the rationale behind its 3-hole design.\n\n"
        )

    if selected_product == "Gorilla Calc Fracture Plating System":
        product_info = (
            "The Gorilla® Calc Fracture Plating System is a product offered by Paragon 28, designed to address fractures of the calcaneus (heel bone). \n"
            "The system provides surgeons with 20 total plates in three families, allowing for a variety of surgical approaches. \n"
            "Key features of the system include: Low Profile Lateral Extensile Approach Plates and Sinus Tarsi Approach Plates: These plates can be contoured intraoperatively according to the surgeon's preference. \n"
            "Versatile Screw Acceptance: All plates accept 2.7 mm, 3.5 mm, and 4.2 mm locking and non-locking polyaxial screws, enabling the surgeon to target the highest quality bone around the fracture site. \n"
            "All holes also have a built-in recess to reduce screw head prominence. Perimeter Plates: These plates are made from CP Grade 4 Titanium, making them malleable and capable of being contoured to surgeon preference. \n"
            "They are designed to be inserted through a lateral extensile approach and can accommodate up to 15 holes for screw placement around comminuted bone. \n"
            "Sinus Tarsi Plates: These plates are made from Titanium (Ti6AI4V-ELI) for improved strength. \n"
            "They are available in two configurations to address fractures of the calcaneus through a minimally invasive approach. \n"
            "The Sinus Tarsi Plate has three holes under the subtalar joint and three anterior holes vertically in line with the calcaneocuboid joint. \n"
            "The Sinus Tarsi Support Plate has the same hole configuration, with an additional posterior arm extending to the posterior tuberosity of the calcaneus for extra fixation. \n"
            "In summary, the Gorilla® Calc Fracture Plating System offers a comprehensive and versatile solution for surgeons dealing with calcaneus fractures, providing a range of plates and screws for different surgical approaches and fracture types. \n\n"
        )

    messages = [
        {"role": "system", "content": product_info +
                                    """You will respond in plain english. You will respond in an informal conversational manner. You will be polite, friendly, and professional but not too formal or corporate.\n\n"
                                    "You value conciseness and brevity. Your responses will be short and to the point. You will not use long, complex sentences.\n\n"
                                    "You will overcome sales objections as if you were teaching a child. You will write responses for 4th-grade reading comprehension.\n\n"
                                    "Your response is designed for a person who has around 8-15 seconds to read it.\n\n"
                                    "You will not put anything inside of brackets as placeholders. For example, do not do this: [briefly mention specific benefits].\n\n"
                                    "You are a medical device sales expert and top performing sales representative. You understand how to handle customer objections professionally.\n\n"
                                    "You address the specific objection entered and deal with it in a structured and logical way. You handle the objection as if you were selling the product yourself.\n\n"                                   
                                    "You are currently working for Paragon 28 as a sales representative. Paragon 28 was established in 2010, as an orthopedic foot and ankle company.\n\n"
                                    "The name “Paragon 28” was chosen to show that we are exclusively a foot and ankle company, with the “28” representing the number of bones in the foot.\n\n"""
        },
        {"role": "user", "content": user_objection},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
            ai_response=response_text
        )
        db.session.add(interaction)
        db.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

    return jsonify({"response_text": response_text, "interaction_id": interaction.id, "regenerate": True})

if __name__ == "__main__":
    with app.app_context():
        create_admin() 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))