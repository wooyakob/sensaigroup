from flask import Blueprint, render_template, request, jsonify
import PyPDF2
import os
import string
from docx import Document

products = Blueprint('products', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/products')
def show_products():
    return render_template('products.html')

@products.route('/upload_endpoint', methods=['POST'])
def upload_file():
    print("Upload endpoint hit")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        print(f"Attempting to save file to {filename}")
        file.save(filename)
        print(f"File saved to {filename}")

    if filename.endswith('.pdf'):
        with open(filename, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            
            printable_text = ''.join(filter(lambda x: x in string.printable, text))

    elif filename.endswith('.doc') or filename.endswith('.docx'):
        doc = Document(filename)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        printable_text = '\n'.join(fullText)
    
    elif filename.endswith('.txt'):
        with open(filename, 'r', encoding='utf-8') as txt_file:
            printable_text = txt_file.read()

    else:
        return jsonify({"error": "File type not supported"})

    text_filename = os.path.join(UPLOAD_FOLDER, file.filename.rsplit('.', 1)[0] + ".txt")
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        text_file.write(printable_text)
                    
    return jsonify({"text_file": text_filename})