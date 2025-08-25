import pytest
from app import app

@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def test_set_get_flow(client):
    r = client.post("/set", json={"key": "a", "value": 1})
    assert r.status_code == 200
    r = client.get("/get/a")
    assert r.status_code == 200
    assert r.get_json()["value"] == 1

def test_tx_rollback_flow(client):
    client.post("/set", json={"key": "a", "value": 1})
    client.post("/begin")
    client.post("/set", json={"key": "a", "value": 2})
    client.post("/rollback")
    r = client.get("/get/a")
    assert r.get_json()["value"] == 1
