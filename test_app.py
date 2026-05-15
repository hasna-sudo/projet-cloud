import pytest
import json
import os
import tempfile
import app as app_module
from app import app

@pytest.fixture
def client():
    tmp_dir = tempfile.mkdtemp()
    tmp_db = os.path.join(tmp_dir, 'test.db')
    app_module.DB = tmp_db
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as c:
        app_module.init_db()
        yield c

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data['status'] == 'ok'

def test_login_page(client):
    r = client.get('/login')
    assert r.status_code == 200

def test_wrong_login(client):
    r = client.post('/login', data={'email':'x@x.com','password':'wrong'})
    assert r.status_code == 200

def test_register_page(client):
    r = client.get('/register')
    assert r.status_code == 200

def test_register_user(client):
    r = client.post('/register', data={
        'name':'TestUser',
        'email':'test@test.com',
        'password':'test123',
        'confirm':'test123'
    })
    assert r.status_code == 200
