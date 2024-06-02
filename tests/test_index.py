from flask.testing import FlaskClient
from unittest.mock import patch

def test_index(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
