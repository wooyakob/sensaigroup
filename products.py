from flask import Blueprint, render_template, request, jsonify
import PyPDF2
import os

products = Blueprint('products', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/products')
def show_products():
    return render_template('products.html')

@products.route('/upload_endpoint', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)

        # Extract text from PDF using PyPDF2 (this is just for the pdf example)
        if filename.endswith('.pdf'):
            with open(filename, 'rb') as pdf_file:
                reader = PyPDF2.PdfFileReader(pdf_file)
                text = ""
                for page_num in range(reader.numPages):
                    text += reader.getPage(page_num).extract_text()
            return jsonify({"text": text})

    return jsonify({"error": "File type not supported"})