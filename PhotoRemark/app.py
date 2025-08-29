from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 请更改为随机密钥

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append({
                'name': filename,
                'url': f"/uploads/{filename}"
            })
    
    return jsonify({'files': saved_files})

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    data = request.json
    image_data = data.get('image_data')
    filename = data.get('filename')
    
    if not image_data or not filename:
        return jsonify({'error': '缺少参数'}), 400
    
    # 移除data URL前缀
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]
    
    # 解码base64图像数据
    image_bytes = base64.b64decode(image_data)
    
    # 安全处理文件名
    safe_filename = secure_filename(filename)
    name, ext = os.path.splitext(safe_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{name}_annotation_{timestamp}{ext}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # 保存图像
    with open(output_path, 'wb') as f:
        f.write(image_bytes)
    
    return jsonify({
        'success': True,
        'message': '标注已保存',
        'filename': output_filename,
        'url': f"/uploads/{output_filename}"
    })

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

if __name__ == '__main__':
    app.run(debug=True)