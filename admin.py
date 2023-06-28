from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import User, Interaction
from extensions import db

admin = Admin(name='My App Admin', template_mode='bootstrap3')

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

def init_admin(app):
    admin.init_app(app)
    admin.add_view(ModelView(User, db.session))
    admin.add_view(InteractionModelView(Interaction, db.session))