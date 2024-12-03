from flask import Flask, request, render_template, url_for, send_from_directory, make_response
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)

# Настраиваем CORS более детально
CORS(app, resources={
    r"/static/*": {
        "origins": ["http://msm-rsde01-ap07:8088"],
        "methods": ["GET", "HEAD", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_uploaded_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            file_url = url_for('static', filename=f'uploads/{filename}')
            files.append({
                'name': filename,
                'url': file_url
            })
    return files

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Файл не выбран'
        file = request.files['file']
        if file.filename == '':
            return 'Файл не выбран'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('static', filename=f'uploads/{filename}')
            return render_template('upload.html', 
                                message=f'Файл успешно загружен!',
                                file_url=request.host_url.rstrip('/') + file_url)
    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    files = get_uploaded_files()
    return render_template('gallery.html', files=files, host_url=request.host_url.rstrip('/'))

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://msm-rsde01-ap07:8088')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/uploads/<filename>')
def serve_static(filename):
    response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
    return response

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000) 