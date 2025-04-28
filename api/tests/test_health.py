import pytest
from flask import Flask
from routes.health import bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_ping_get(client):
    """Test GET request to /health/ping endpoint"""
    response = client.get("/health/ping")
    assert response.status_code == 200
    assert response.json["data"] == {"ping": "pong"}


def test_ping_response_format(client):
    """Test response format of /health/ping endpoint"""
    response = client.get("/health/ping")
    assert response.is_json
    assert isinstance(response.json, dict)
    assert "ping" in response.json["data"]
    assert response.json["data"]["ping"] == "pong"
