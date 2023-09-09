from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from models import User, Interaction, Product
from extensions import db

admin = Admin(name='My App Admin', template_mode='bootstrap3')

class InteractionModelView(ModelView):
    column_list = ('id', 'user', 'objection', 'ai_response', 'rating', 'timestamp')
    column_labels = {
        'user': 'User',
        'objection': 'Objection',
        'ai_response': 'AI Response',
        'rating': 'Rating',
        'timestamp': 'Timestamp'
    }
    column_searchable_list = ['user.first_name', 'user.last_name', 'user.email', 'user.username']

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

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

class ProductModelView(ModelView):
    column_list = ('id', 'product_name', 'slug', 'product_info', 'design_rationale')
    column_labels = {
        'product_name': 'Product Name',
        'slug': 'Slug',
        'product_info': 'Product Info',
        'design_rationale': 'Design Rationale'
    }
    column_searchable_list = ['product_name']

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

admin.add_view(ProductModelView(Product, db.session))