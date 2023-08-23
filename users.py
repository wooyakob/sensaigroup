from flask import Blueprint, render_template, request, redirect, url_for
from app import User
from extensions import db

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

        return redirect(url_for('admin_dashboard'))

    return render_template('users.html')
