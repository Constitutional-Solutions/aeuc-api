"""
Integration tests for the /glyphs endpoints.
Uses FastAPI's TestClient (HTTPX under the hood — no running server needed).
"""
from fastapi.testclient import TestClient
from aeuc_api.main import app
from aeuc_api.registry import registry

client = TestClient(app)


def setup_function():
    """Wipe registry state before each test to ensure isolation."""
    registry.glyphs_144k.clear()
    registry.code_to_id.clear()
    for cat in registry.category_index:
        registry.category_index[cat].clear()
    registry.change_history.clear()
    registry._update_hash()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert len(body["current_hash"]) == 64


def test_add_and_get_glyph():
    payload = {
        "id": 1,
        "code": "GEO_TETRA_A",
        "category": "GEOMETRY",
        "description": "Base tetrahedron cell A",
    }
    r = client.post("/glyphs", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["code"] == "GEO_TETRA_A"

    r2 = client.get("/glyphs/1")
    assert r2.status_code == 200
    assert r2.json()["code"] == "GEO_TETRA_A"


def test_get_by_code():
    client.post("/glyphs", json={"id": 5, "code": "ZERO", "category": "SPECIAL", "description": "Empty"})
    r = client.get("/glyphs/code/ZERO")
    assert r.status_code == 200
    assert r.json()["id"] == 5


def test_update_glyph():
    client.post("/glyphs", json={"id": 10, "code": "UPD", "category": "SPECIAL", "description": "old"})
    r = client.patch("/glyphs/10", json={"description": "updated description"})
    assert r.status_code == 200
    assert r.json()["description"] == "updated description"


def test_update_glyph_multiple_fields():
    client.post("/glyphs", json={"id": 11, "code": "MULTI", "category": "SPECIAL", "description": "orig"})
    r = client.patch("/glyphs/11", json={"description": "new desc", "version": "2.0.0"})
    assert r.status_code == 200
    body = r.json()
    assert body["description"] == "new desc"


def test_update_glyph_unknown_field_rejected():
    client.post("/glyphs", json={"id": 12, "code": "UNK", "category": "SPECIAL", "description": "x"})
    r = client.patch("/glyphs/12", json={"nonexistent_field": "value"})
    assert r.status_code == 422


def test_audit_hash_before_captured_before_mutation():
    """hash_before in an audit entry must equal the hash from just before the mutation."""
    registry.change_history.clear()
    registry._update_hash()
    hash_before_add = registry.current_hash
    client.post("/glyphs", json={"id": 70, "code": "AUDIT_TEST", "category": "SPECIAL", "description": "y"})
    entry = registry.change_history[-1]
    assert entry["hash_before"] == hash_before_add
    assert entry["hash_after"] != hash_before_add
    assert entry["hash_after"] == registry.current_hash


def test_delete_glyph():
    client.post("/glyphs", json={"id": 20, "code": "DEL", "category": "SPECIAL", "description": "to delete"})
    r = client.delete("/glyphs/20")
    assert r.status_code == 204
    assert client.get("/glyphs/20").status_code == 404


def test_duplicate_id_rejected():
    client.post("/glyphs", json={"id": 30, "code": "DUP", "category": "SPECIAL", "description": "first"})
    r = client.post("/glyphs", json={"id": 30, "code": "DUP2", "category": "SPECIAL", "description": "second"})
    assert r.status_code == 409


def test_list_by_category():
    client.post("/glyphs", json={"id": 40, "code": "H1", "category": "HARMONIC", "description": "h1"})
    client.post("/glyphs", json={"id": 41, "code": "H2", "category": "HARMONIC", "description": "h2"})
    r = client.get("/glyphs?category=HARMONIC")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_audit_log_grows():
    client.post("/glyphs", json={"id": 50, "code": "AUD", "category": "SPECIAL", "description": "audit"})
    r = client.get("/audit")
    assert r.json()["total"] >= 1


def test_hash_changes_on_mutation():
    h1 = client.get("/health").json()["current_hash"]
    client.post("/glyphs", json={"id": 60, "code": "HASH", "category": "SPECIAL", "description": "x"})
    h2 = client.get("/health").json()["current_hash"]
    assert h1 != h2
