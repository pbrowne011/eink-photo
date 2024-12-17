import pytest
from app import create_app
from pathlib import Path
import io

@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_upload_no_file(client):
    response = client.post('/upload')
    assert response.status_code == 400
    assert b'No file part' in response.data

def test_upload_success(client):
    data = {'file': (io.BytesIO(b'test image content'), 'test.jpg')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert Path('photos/originals/test.jpg').exists()
