import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.auth import clear_login_failures, hash_password, verify_password

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_password_hashing():
    pw = "SuperSecretPassword123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("ok", "degraded")
    assert data["app"] == settings.app_name

def test_session_unauthenticated(client):
    res = client.get("/api/session")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is False
    assert data["username"] is None
    assert "ai_provider" in data

def test_dashboard_unauthorized(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 401

def test_csrf_blocking(client):
    # Cross-site POST request should be blocked by Sec-Fetch-Site check
    res = client.post(
        "/api/login",
        data={"username": "admin", "password": "any"},
        headers={"sec-fetch-site": "cross-site"}
    )
    assert res.status_code == 403
    assert "Cross-site" in res.json()["detail"]

def test_login_rate_limiting(client):
    # Clear prior failed attempts for clean test run
    rate_key = "testclient:ratelimit_user"
    clear_login_failures(rate_key)

    for i in range(5):
        res = client.post("/api/login", data={"username": "ratelimit_user", "password": "wrong"})
        assert res.status_code == 401

    # 6th attempt should be blocked with 429
    blocked_res = client.post("/api/login", data={"username": "ratelimit_user", "password": "wrong"})
    assert blocked_res.status_code == 429
    assert "Terlalu banyak percobaan" in blocked_res.json()["detail"]

    clear_login_failures(rate_key)

def test_login_and_product_flow(client):
    # Login with valid credentials
    login_res = client.post("/api/login", data={
        "username": settings.admin_username,
        "password": settings.admin_password
    })
    assert login_res.status_code == 200
    assert login_res.json() == {"ok": True}

    # Verify session is now active
    session_res = client.get("/api/session")
    assert session_res.status_code == 200
    assert session_res.json()["authenticated"] is True
    assert session_res.json()["username"] == settings.admin_username

    # Access dashboard
    dash_res = client.get("/api/dashboard")
    assert dash_res.status_code == 200
    data = dash_res.json()
    assert "total_products" in data
    assert len(data["platforms"]) == 3

    # Create a product
    prod_res = client.post("/api/products", json={
        "name": "Kemeja Flannel Preloved Uniqlo",
        "price": 95000,
        "condition": "Preloved - Sangat Baik",
        "stock": 1,
        "description": "Kemeja flannel kotak-kotak size M kondisi mulus tanpa minus."
    })
    assert prod_res.status_code == 201
    prod_data = prod_res.json()
    assert prod_data["id"] is not None
    assert prod_data["name"] == "Kemeja Flannel Preloved Uniqlo"

    # List products
    list_res = client.get("/api/products")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["name"] == "Kemeja Flannel Preloved Uniqlo" for item in items)

    # Logout
    logout_res = client.post("/api/logout")
    assert logout_res.status_code == 200

    # Verify session is unauthenticated
    session_after = client.get("/api/session").json()
    assert session_after["authenticated"] is False
    assert session_after["username"] is None
