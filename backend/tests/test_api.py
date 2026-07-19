import os
os.environ.setdefault("ROI_API_KEY", "test-key")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
API_KEY = "test-key"


def test_health_no_auth_required():
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_snapshot_requires_api_key():
    resp = client.get("/api/snapshot")
    assert resp.status_code == 401


def test_snapshot_with_valid_key():
    resp = client.get("/api/snapshot", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["placements"]) > 0


def test_roi_report_with_valid_key():
    resp = client.get("/api/roi-report", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    body = resp.json()
    assert "scores" in body
    assert len(body["scores"]) > 0


def test_rate_limit_blocks_excess_requests():
    statuses = [
        client.get("/api/snapshot", headers={"X-API-Key": API_KEY}).status_code
        for _ in range(65)
    ]
    assert 429 in statuses
