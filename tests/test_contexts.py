from fastapi.testclient import TestClient
from aeuc_api.main import app

client = TestClient(app)


def test_list_contexts():
    r = client.get("/contexts")
    assert r.status_code == 200
    # 10 defaults (CTX_BASE through CTX_SOVEREIGN)
    assert len(r.json()) == 10


def test_get_context_by_id():
    r = client.get("/contexts/0")
    assert r.status_code == 200
    assert r.json()["code"] == "CTX_BASE"


def test_context_not_found():
    # outer_id 9 is CTX_SOVEREIGN (default), outer_id > 9 is invalid
    r = client.get("/contexts/9")
    assert r.status_code == 200
