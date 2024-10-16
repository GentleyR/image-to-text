from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename

import subprocess

def check_tesseract_installation():
    try:
        result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE)
        print("Tesseract version:", result.stdout.decode('utf-8'))
    except FileNotFoundError:
        print("Tesseract is not installed or not in the PATH.")

check_tesseract_installation()

app = Flask(__name__)

#configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get the selected language from the form
        language = request.form.get('language', 'eng')

        # Open the image using PIL
        try:
            img = Image.open(filepath)
            # Perform OCR using pytesseract with the specified language
            extracted_text = pytesseract.image_to_string(img, lang=language)
        except Exception as e:
            extracted_text = f"An error occurred while processing the image: {e}"

        # Optionally, delete the uploaded file after processing
        os.remove(filepath)

        return render_template('index.html', extracted_text=extracted_text)
    else:
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))