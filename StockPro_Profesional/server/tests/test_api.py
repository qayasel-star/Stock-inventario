"""Pruebas de humo para la API de licencias. No sustituyen una auditoría de seguridad."""
import os
import secrets
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient

os.environ.setdefault("STOCKPRO_OWNER_TOKEN", "test-owner-token-please-change")
os.environ.setdefault("STOCKPRO_DB", "/tmp/stockpro-test-" + secrets.token_hex(6) + ".db")
from main import app

client = TestClient(app)
OWNER = {"Authorization": "Bearer " + os.environ["STOCKPRO_OWNER_TOKEN"]}
DEVICE = "device-test-123456789"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["ok"] is True


def test_owner_routes_require_auth():
    assert client.get("/v1/owner/licenses").status_code == 401


def test_trial_is_30_days_and_stable():
    first = client.post("/v1/trial", json={"device_id": DEVICE})
    second = client.post("/v1/trial", json={"device_id": DEVICE})
    assert first.status_code == second.status_code == 200
    assert first.json()["expires_at"] == second.json()["expires_at"]
    assert first.json()["status"] == "active"


def test_issue_validate_renew_revoke():
    issued = client.post("/v1/owner/licenses", headers=OWNER, json={
        "customer": "Cliente de prueba", "device_id": DEVICE, "days": 30, "plan": "mensual"
    })
    assert issued.status_code == 200
    lid = issued.json()["id"]
    assert client.post("/v1/license/validate", json={"device_id": DEVICE}).json()["status"] == "licensed"
    renewed = client.post(f"/v1/owner/licenses/{lid}/renew", headers=OWNER, json={"days": 30})
    assert renewed.status_code == 200
    revoked = client.post(f"/v1/owner/licenses/{lid}/revoke", headers=OWNER)
    assert revoked.status_code == 200 and revoked.json()["status"] == "revoked"
