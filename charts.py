from flask import Blueprint, render_template, request, jsonify
from extensions import db
from models import Interaction

charts = Blueprint('charts', __name__)

@charts.route('/api/objections_data', methods=['GET'])
def objections_data():
    total_objections = db.session.query(Interaction).filter(Interaction.objection.isnot(None)).count()
    total_product_objections = db.session.query(Interaction).filter(Interaction.product_objection.isnot(None)).count()
    total_product_advice = db.session.query(Interaction).filter(Interaction.product_advice.isnot(None)).count()


    data = {
        'labels': ['Objections', 'Product Objections', 'Product Questions'],
        'datasets': [{
            'data': [total_objections, total_product_objections, total_product_advice],
            'backgroundColor': ['red', 'black', 'orange']
        }]
    }
    return jsonify(data)

@charts.route('/api/total_users')
def total_users():
    total = User.query.count()
    return jsonify(total=total)




