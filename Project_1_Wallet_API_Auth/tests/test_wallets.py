import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_authenticated_headers():
    unique_email = f"wallet_tester_{int(time.time() * 1000)}@example.com"
    pwd = "WalletTestPassword123!"
    # Signup
    signup_res = client.post(
        "/auth/signup",
        json={
            "full_name": "Wallet Tester",
            "email": unique_email,
            "password": pwd,
            "country": "Germany",
        },
    )
    assert signup_res.status_code == 201

    # Login
    login_res = client.post(
        "/auth/login",
        json={"email": unique_email, "password": pwd},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_wallets_unauthenticated():
    # Calling /wallets/me without token must be rejected with 401 or 403
    res = client.get("/wallets/me")
    assert res.status_code in (401, 403)


def test_wallets_me_and_creation():
    headers = get_authenticated_headers()

    # User starts with default primary wallet
    res = client.get("/wallets/me", headers=headers)
    assert res.status_code == 200
    wallets = res.json()
    assert len(wallets) >= 1
    primary = wallets[0]
    assert primary["wallet_type"] == "Primary"
    assert primary["currency"] == "USD"
    primary_id = primary["wallet_id"]

    # Check balance endpoint for own wallet
    bal_res = client.get(f"/wallets/{primary_id}/balance", headers=headers)
    assert bal_res.status_code == 200
    assert bal_res.json()["wallet_id"] == primary_id
    assert "balance" in bal_res.json()

    # Create additional Savings EUR wallet
    create_res = client.post(
        "/wallets",
        headers=headers,
        json={"currency": "EUR", "wallet_type": "Savings"},
    )
    assert create_res.status_code == 201
    new_wallet = create_res.json()
    assert new_wallet["currency"] == "EUR"
    assert new_wallet["wallet_type"] == "Savings"

    # User now has at least 2 wallets
    res2 = client.get("/wallets/me", headers=headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 2


def test_wallet_unauthorized_access():
    user1_headers = get_authenticated_headers()
    user2_headers = get_authenticated_headers()

    # User 1 gets their wallet
    u1_wallets = client.get("/wallets/me", headers=user1_headers).json()
    u1_wallet_id = u1_wallets[0]["wallet_id"]

    # User 2 tries to access User 1's wallet balance -> Forbidden (403)
    forbidden_res = client.get(f"/wallets/{u1_wallet_id}/balance", headers=user2_headers)
    assert forbidden_res.status_code == 403


def test_wallet_not_found():
    headers = get_authenticated_headers()
    # High invalid ID
    res = client.get("/wallets/999999999/balance", headers=headers)
    assert res.status_code == 404

