from flask import Blueprint, request, jsonify, render_template, send_from_directory
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heif', 'heic', 'bmp', 'pdf'}

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / 'photos' / 'originals'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        try:
            save_path = Path(UPLOAD_FOLDER) / file.filename
            file.save(save_path)
            logger.info(f'Saved file: {save_path}')
            return jsonify({'message': 'File uploaded successfully'}), 200
        except Exception as e:
            logger.error(f'Error saving file: {e}')
            return jsonify({'error': 'Error saving file'}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@main.route('/photos/list')
def list_photos():
    try:
        photos = list()
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                photos.append({
                    'filename': filename,
                    'path': f'/photos/originals/{filename}'
                })
        logger.info(f'Loaded {len(photos)} photos')
        return jsonify(photos)
    except Exception as e:
        logger.error(f'Error loading files: {e}')
        return jsonify({'error': 'Error listing files'}), 400

@main.route('/photos/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    try:
        file_path =  UPLOAD_FOLDER / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f'Deleted file {filename}')
            return jsonify({'message': f'Deleted {filename}'}), 200
        logger.error(f'Error deleting {filename}: file not found')
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f'Error deleteing {filename}: {e}')
        return jsonify({'error': 'Error deleting file'}), 500

@main.route('/photos/originals/<filename>')
def serve_photo(filename):
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type'}), 400
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f'Error serving file {filename}: {e}')
        return jsonify({'error': 'Error serving file'}), 500
