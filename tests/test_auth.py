import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from core.security import ALGORITHM, SECRET_KEY
from main import app

client = TestClient(app)


def get_token(username: str, password: str) -> str:
    resp = client.post("/login", json={"username": username, "password": password})
    return resp.json()["data"]["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def make_expired_token(username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": username, "role": role, "iat": now - timedelta(minutes=30), "exp": now - timedelta(minutes=10)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---- 2 test token ----

def test_missing_token_returns_401():
    resp = client.get("/exams")
    assert resp.status_code == 401


def test_expired_token_returns_401():
    token = make_expired_token("student01", "user")
    resp = client.get("/exams", headers=auth_header(token))
    assert resp.status_code == 401
    assert resp.json()["error"] == "token_expired"


# ---- 2 test role ----

def test_user_role_forbidden_on_admin_endpoint():
    token = get_token("student01", "pass123")
    resp = client.post("/admin/exams", json={"name": "Ca thi mới"}, headers=auth_header(token))
    assert resp.status_code == 403


def test_admin_role_allowed_on_admin_endpoint():
    token = get_token("admin01", "admin123")
    resp = client.post("/admin/exams", json={"name": "Ca thi mới"}, headers=auth_header(token))
    assert resp.status_code == 201


# ---- 2 test quyền sở hữu dữ liệu ----

def test_user_can_view_own_results():
    token = get_token("student01", "pass123")
    resp = client.get("/users/student01/results", headers=auth_header(token))
    assert resp.status_code == 200


def test_user_cannot_view_others_results():
    token = get_token("student01", "pass123")
    resp = client.get("/users/student02/results", headers=auth_header(token))
    assert resp.status_code == 403


# ---- 1 test CORS preflight ----

def test_options_preflight_does_not_require_jwt():
    resp = client.options(
        "/admin/exams",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code in (200, 204)


# ---- 1 test endpoint công khai ----

def test_health_endpoint_is_public():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "up"


# ---- bonus: bẫy path parameter (exam_id) qua Dependency ----

def test_admin_lock_exam_with_path_param_works():
    token = get_token("admin01", "admin123")
    resp = client.patch("/admin/exams/1/lock", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["locked"] is True


# ---- bonus: admin xem được toàn bộ kết quả ----

def test_admin_can_view_all_results():
    token = get_token("admin01", "admin123")
    resp = client.get("/admin/results", headers=auth_header(token))
    assert resp.status_code == 200
