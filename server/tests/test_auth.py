from fastapi.testclient import TestClient


def test_seeded_user_login(client: TestClient):
    payload = {"email": "test@example.com", "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["is_active"] is True
    assert data["user"]["is_verified"] is True


def test_seeded_admin_login(client: TestClient):
    payload = {"email": "admin@example.com", "password": "adminpassword"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_get_me_profile(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "test@example.com"


def test_invalid_login_returns_401(client: TestClient):
    payload = {"email": "test@example.com", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
