from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
fake_auth_token = "abracadabra"


def test_read_test():
    response = client.get("/test", headers={"X-Token": fake_auth_token})
    assert response.status_code == 200
    assert response.json() =={"msg": "Hello World"}

