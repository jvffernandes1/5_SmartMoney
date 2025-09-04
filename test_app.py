import pytest
from app import app as flask_app

def test_index_route():
    client = flask_app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Smart Money' in response.data

def test_login_route():
    client = flask_app.test_client()
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Entrar' in response.data

def test_register_route():
    client = flask_app.test_client()
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Cadastrar' in response.data
