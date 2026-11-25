dimport time
import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_user_and_get_wallet(email_prefix: str, currency: str = "USD"):
    unique_email = f"{email_prefix}_{int(time.time() * 1000)}@example.com"
    pwd = "SecurePassword123!"

    # Signup
    signup_res = client.post(
        "/auth/signup",
        json={
            "full_name": f"User {email_prefix}",
            "email": unique_email,
            "password": pwd,
            "country": "United States",
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
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch wallets
    wallets_res = client.get("/wallets/me", headers=headers)
    assert wallets_res.status_code == 200
    wallets = wallets_res.json()
    primary_wallet = wallets[0]

    # If requested currency is different from USD, create matching wallet
    if currency != "USD":
        create_w_res = client.post(
            "/wallets",
            headers=headers,
            json={"currency": currency, "wallet_type": "Savings"},
        )
        assert create_w_res.status_code == 201
        wallet_to_use = create_w_res.json()
    else:
        wallet_to_use = primary_wallet

    return headers, wallet_to_use


def test_deposit_and_withdrawal():
    headers, wallet = create_user_and_get_wallet("dep_with_user")
    wid = wallet["wallet_id"]

    # 1. Deposit $250.00
    dep_res = client.post(
        f"/wallets/{wid}/deposit",
        headers=headers,
        json={"amount": 250.00},
    )
    assert dep_res.status_code == 200
    dep_data = dep_res.json()
    assert dep_data["is_cached"] is False
    assert dep_data["transaction"]["transaction_type"] == "Deposit"
    assert dep_data["transaction"]["sender_wallet_id"] is None
    assert dep_data["transaction"]["receiver_wallet_id"] == wid
    assert Decimal(str(dep_data["updated_balance"])) == Decimal("250.00")

    # 2. Withdraw $50.00
    with_res = client.post(
        f"/wallets/{wid}/withdraw",
        headers=headers,
        json={"amount": 50.00},
    )
    assert with_res.status_code == 200
    with_data = with_res.json()
    assert with_data["transaction"]["transaction_type"] == "Withdrawal"
    assert with_data["transaction"]["sender_wallet_id"] == wid
    assert with_data["transaction"]["receiver_wallet_id"] is None
    assert Decimal(str(with_data["updated_balance"])) == Decimal("200.00")

    # 3. Withdraw overdrawn amount ($300.00) -> Must fail with 400
    over_res = client.post(
        f"/wallets/{wid}/withdraw",
        headers=headers,
        json={"amount": 300.00},
    )
    assert over_res.status_code == 400
    assert "insufficient balance" in over_res.json()["detail"].lower()


def test_atomic_transfer_success():
    h_sender, w_sender = create_user_and_get_wallet("sender_user")
    h_receiver, w_receiver = create_user_and_get_wallet("receiver_user")

    s_id = w_sender["wallet_id"]
    r_id = w_receiver["wallet_id"]

    # Deposit funds to sender
    client.post(f"/wallets/{s_id}/deposit", headers=h_sender, json={"amount": 100.00})

    # Transfer $40.00 to receiver
    key = str(uuid.uuid4())
    transfer_res = client.post(
        f"/wallets/{s_id}/transfer",
        headers=h_sender,
        json={
            "receiver_wallet_id": r_id,
            "amount": 40.00,
            "idempotency_key": key,
        },
    )
    assert transfer_res.status_code == 200
    t_data = transfer_res.json()
    assert t_data["is_cached"] is False
    assert Decimal(str(t_data["updated_balance"])) == Decimal("60.00")
    assert t_data["transaction"]["transaction_type"] == "Transfer"

    # Verify receiver balance is now $40.00
    r_bal_res = client.get(f"/wallets/{r_id}/balance", headers=h_receiver)
    assert r_bal_res.status_code == 200
    assert Decimal(str(r_bal_res.json()["balance"])) == Decimal("40.00")


def test_transfer_insufficient_funds():
    h_sender, w_sender = create_user_and_get_wallet("broke_sender")
    h_receiver, w_receiver = create_user_and_get_wallet("receiver_user_2")

    # Sender balance is 0.00, try to transfer $100.00
    key = str(uuid.uuid4())
    res = client.post(
        f"/wallets/{w_sender['wallet_id']}/transfer",
        headers=h_sender,
        json={
            "receiver_wallet_id": w_receiver["wallet_id"],
            "amount": 100.00,
            "idempotency_key": key,
        },
    )
    assert res.status_code == 400
    assert "insufficient balance" in res.json()["detail"].lower()


def test_transfer_to_self_rejected():
    h_user, w = create_user_and_get_wallet("self_transfer_user")
    wid = w["wallet_id"]

    client.post(f"/wallets/{wid}/deposit", headers=h_user, json={"amount": 50.00})

    # Transfer to self must fail
    res = client.post(
        f"/wallets/{wid}/transfer",
        headers=h_user,
        json={
            "receiver_wallet_id": wid,
            "amount": 10.00,
            "idempotency_key": str(uuid.uuid4()),
        },
    )
    assert res.status_code == 400
    assert "same wallet" in res.json()["detail"].lower()


def test_transfer_currency_mismatch_rejected():
    h_usd, w_usd = create_user_and_get_wallet("usd_user", currency="USD")
    h_eur, w_eur = create_user_and_get_wallet("eur_user", currency="EUR")

    client.post(f"/wallets/{w_usd['wallet_id']}/deposit", headers=h_usd, json={"amount": 100.00})

    # Transfer USD to EUR wallet
    res = client.post(
        f"/wallets/{w_usd['wallet_id']}/transfer",
        headers=h_usd,
        json={
            "receiver_wallet_id": w_eur["wallet_id"],
            "amount": 25.00,
            "idempotency_key": str(uuid.uuid4()),
        },
    )
    assert res.status_code == 400
    assert "currency mismatch" in res.json()["detail"].lower()


def test_idempotency_key_replay_prevents_double_charge():
    h_sender, w_sender = create_user_and_get_wallet("idempotency_sender")
    h_receiver, w_receiver = create_user_and_get_wallet("idempotency_receiver")

    s_id = w_sender["wallet_id"]
    r_id = w_receiver["wallet_id"]

    # Deposit $100.00
    client.post(f"/wallets/{s_id}/deposit", headers=h_sender, json={"amount": 100.00})

    reusable_key = str(uuid.uuid4())
    payload = {
        "receiver_wallet_id": r_id,
        "amount": 30.00,
        "idempotency_key": reusable_key,
    }

    # 1. First execution
    first_res = client.post(f"/wallets/{s_id}/transfer", headers=h_sender, json=payload)
    assert first_res.status_code == 200
    first_data = first_res.json()
    assert first_data["is_cached"] is False
    assert Decimal(str(first_data["updated_balance"])) == Decimal("70.00")
    txn_id_first = first_data["transaction"]["transaction_id"]

    # 2. Simulated Network Retry with the SAME idempotency key
    second_res = client.post(f"/wallets/{s_id}/transfer", headers=h_sender, json=payload)
    assert second_res.status_code == 200
    second_data = second_res.json()
    assert second_data["is_cached"] is True
    # Crucial assertion: Transaction ID must match the original transaction
    assert second_data["transaction"]["transaction_id"] == txn_id_first

    # 3. CRUCIAL CHECK: Balance of sender must STILL be 70.00 (NOT 40.00)
    bal_res = client.get(f"/wallets/{s_id}/balance", headers=h_sender)
    assert Decimal(str(bal_res.json()["balance"])) == Decimal("70.00")


def test_transaction_audit_trail_history():
    h_user, w = create_user_and_get_wallet("audit_user")
    wid = w["wallet_id"]

    # Execute deposit and withdrawal
    client.post(f"/wallets/{wid}/deposit", headers=h_user, json={"amount": 150.00})
    client.post(f"/wallets/{wid}/withdraw", headers=h_user, json={"amount": 25.00})

    # Fetch audit log
    txns_res = client.get(f"/wallets/{wid}/transactions", headers=h_user)
    assert txns_res.status_code == 200
    txns = txns_res.json()
    assert len(txns) >= 2
    types = [t["transaction_type"] for t in txns]
    assert "Deposit" in types
    assert "Withdrawal" in types
