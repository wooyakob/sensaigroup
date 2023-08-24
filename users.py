from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app import User
from extensions import db
from flask_mail import Message

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/admin/createuser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([first_name, last_name, email, username, password]):
            return render_template('users.html', error_message='Missing required fields')

        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, is_admin=False)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        if new_user:
            login_url = request.url_root.rstrip('/') + url_for('login')
            msg = Message("Welcome to SensAI", recipients=[email])
            msg.body = (f"Thank you for joining SensAI! "
                        f"Here's a link to login: {login_url}\n\n"
                        f"Your credentials:\n"
                        f"Username: {username}\n"
                        f"Password: {password}")
            current_app.extensions['mail'].send(msg)


        return redirect(url_for('admin_dashboard'))

    return render_template('users.html')