from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import PyPDF2
import os
import string
from docx import Document
from app import db
from models import Product
from flask_login import current_user

products = Blueprint('products', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/products')
def show_products():
    user = current_user
    user_products = Product.query.filter_by(user_id=user.id).all()
    return render_template('products.html', products=user_products)

@products.route('/upload_endpoint', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    printable_text = ""
    if file and allowed_file(file.filename):
        if file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                printable_text += reader.pages[page_num].extract_text()

        elif file.filename.endswith('.doc') or file.filename.endswith('.docx'):
            doc = Document(file.stream)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
            printable_text = '\n'.join(fullText)

        elif file.filename.endswith('.txt'):
            printable_text = file.stream.read().decode('utf-8')

        else:
            return jsonify({"error": "File type not supported"})
    else:
        return jsonify({"error": "Invalid file"})

    printable_text = ''.join(filter(lambda x: x in string.printable, printable_text))
                    
    return jsonify({"text": printable_text})  # Return the extracted text

@products.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_info = request.form['product_info']
        text_file_path = request.form.get('text_file_path', None)

        # Basic validation
        if not product_name or not product_info:
            flash('Product name and info are required!')
            return redirect(url_for('add_product'))

        # Read context from text file (extracted from PDF)
        context = request.form.get('text_file_path', None)  # This will now have the actual text instead of a path
        if text_file_path and os.path.exists(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                context = f.read()
            # Optionally, delete the text file afterward if not needed
            os.remove(text_file_path)

        # Create a new product with the extracted context
        new_product = Product(product_name=product_name, product_info=product_info, context=context, user_id=current_user.id,)
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('products.html')