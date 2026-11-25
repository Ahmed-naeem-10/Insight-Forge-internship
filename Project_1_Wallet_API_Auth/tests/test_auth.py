import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    assert "documentation" in res.json()

    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_auth_signup_success():
    payload = {
        "full_name": "Test User Alpha",
        "email": "test_alpha@example.com",
        "password": "Password123!",
        "country": "United States",
        "phone_number": "+1234567890",
    }
    res = client.post("/auth/signup", json=payload)
    # If user already exists from previous test run, status might be 400 or 201
    if res.status_code == 400:
        # Already exists, try with unique timestamp
        import time
        unique_email = f"test_alpha_{int(time.time())}@example.com"
        payload["email"] = unique_email
        res = client.post("/auth/signup", json=payload)

    assert res.status_code == 201
    data = res.json()
    assert "user_id" in data
    assert data["email"] == payload["email"].lower()
    assert data["full_name"] == payload["full_name"]
    # Critical security check: password_hash must NEVER be exposed
    assert "password_hash" not in data
    assert "password" not in data


def test_auth_signup_duplicate_email():
    payload = {
        "full_name": "Duplicate Tester",
        "email": "duplicate_check@example.com",
        "password": "SecurePassword123!",
        "country": "United Kingdom",
    }
    first_res = client.post("/auth/signup", json=payload)
    assert first_res.status_code in (201, 400)

    # Second attempt with same email must fail
    second_res = client.post("/auth/signup", json=payload)
    assert second_res.status_code == 400
    assert "already exists" in second_res.json()["detail"].lower()


def test_auth_login_success_and_token():
    email = "login_tester@example.com"
    password = "CorrectPassword123!"

    # Ensure user exists
    client.post(
        "/auth/signup",
        json={
            "full_name": "Login Tester",
            "email": email,
            "password": password,
            "country": "Canada",
        },
    )

    # Successful login
    res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    # Test /auth/me with the token
    token = data["access_token"]
    me_res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email


def test_auth_login_invalid_password():
    res = client.post(
        "/auth/login",
        json={"email": "nonexistent_or_wrong@example.com", "password": "WrongPassword!"},
    )
    assert res.status_code == 401

