from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
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
        available_photos = current_app.display_controller.get_available_photos()
        photos = []
        for photo in available_photos:
            photos.append({
                'filename': photo['filename'],
                'path': f'/photos/originals/{photo["filename"]}'
            })
        logger.info(f'Loaded {len(photos)} photos')
        return jsonify(photos)
    except Exception as e:
        logger.error(f'Error loading files: {e}')
        return jsonify({'error': 'Error listing files'}), 400

@main.route('/photos/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    try:
        file_path = UPLOAD_FOLDER / filename
        if file_path.exists():
            file_path.unlink()
            # Also clean up corresponding display file if it exists
            display_path = Path('photos/display') / f"{file_path.stem}.bmp"
            if display_path.exists():
                display_path.unlink()
                logger.info(f'Deleted converted file: {display_path}')
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

@main.route('/photos/status')
def photos_status():
    status = current_app.display_controller.get_status()
    if status:
        return jsonify(status), 200
    return jsonify({'error': 'Error getting photos status'}), 500

@main.route('/photos/display/<filename>', methods=['POST'])
def display_photo(filename):
    try:
        if current_app.display_controller.display_photo(filename):
            return jsonify({'message': f'Displaying {filename}'}), 200
        return jsonify({'error': 'Failed to display photo'}), 500
    except Exception as e:
        logger.error(f'Error displaying photo {filename}: {e}')
        return jsonify({'error': 'Error displaying photo'}), 500

@main.route('/photos/convert/<filename>', methods=['POST'])
def convert_photo(filename):
    try:
        if current_app.display_controller.convert_photo(filename):
            return jsonify({'message': f'Converted {filename}'}), 200
        return jsonify({'error': 'Failed to convert photo'}), 500
    except Exception as e:
        logger.error(f'Error converting photo {filename}: {e}')
        return jsonify({'error': 'Error converting photo'}), 500
    
