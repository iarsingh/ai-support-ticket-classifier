from fastapi.testclient import TestClient
from aiticket.main import app

client = TestClient(app)


def test_labels():
    assert client.post("/classify", json={"text": 'invoice charge is wrong'}).json()["label"] == "billing"
    assert client.post("/classify", json={"text": 'cluster is down'}).json()["label"] == "outage"


def test_empty_is_refused():
    assert client.post("/classify", json={"text": "  "}).status_code == 422
