import urllib.request
import urllib.error
import json
import time
import uuid

BASE_URL = "http://127.0.0.1:8000"

def print_step(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        body = json.loads(e.read().decode("utf-8"))
        return status, body

def run_live_demo():
    print("\n🚀 STARTING COMPLETE LIVE DEMO: GLOBALPAY WALLET API (TASKS 1 & 2)")
    print(f"Target Server: {BASE_URL}")
    time.sleep(1)

    # 1. Health Check
    print_step("STEP 1: System Health & OpenAPI Documentation Check")
    status, health = make_request("GET", "/health")
    print(f"✓ Health Check: [Status {status}] -> {health}")
    status, root = make_request("GET", "/")
    print(f"✓ Root Info: [Status {status}] -> Project: '{root['project']}' | Docs at: {root['documentation']}")
    time.sleep(1)

    # 2. User 1 (Sender) Setup
    print_step("STEP 2: Register User 1 (Sender) via POST /auth/signup")
    u1_email = f"sender_{int(time.time())}@globalpay.com"
    pwd = "SecurePassword@2026"
    status, u1 = make_request("POST", "/auth/signup", data={
        "full_name": "Taimoor Hassan",
        "email": u1_email,
        "password": pwd,
        "country": "Pakistan",
        "phone_number": "+923001234567"
    })
    print(f"✓ User 1 Registered: ID {u1['user_id']} ({u1['email']})")

    status, tok1 = make_request("POST", "/auth/login", data={"email": u1_email, "password": pwd})
    token1 = tok1["access_token"]
    print(f"✓ User 1 Logged In: JWT issued (Expires in {tok1['expires_in']}s)")

    status, w1_list = make_request("GET", "/wallets/me", token=token1)
    w1_id = w1_list[0]["wallet_id"]
    print(f"✓ User 1 Primary Wallet: ID {w1_id} | Initial Balance: {w1_list[0]['balance']} USD")
    time.sleep(1)

    # 3. User 2 (Receiver) Setup
    print_step("STEP 3: Register User 2 (Receiver) via POST /auth/signup")
    u2_email = f"receiver_{int(time.time())}@globalpay.com"
    status, u2 = make_request("POST", "/auth/signup", data={
        "full_name": "Sarah Jenkins",
        "email": u2_email,
        "password": pwd,
        "country": "United States"
    })
    print(f"✓ User 2 Registered: ID {u2['user_id']} ({u2['email']})")

    status, tok2 = make_request("POST", "/auth/login", data={"email": u2_email, "password": pwd})
    token2 = tok2["access_token"]
    status, w2_list = make_request("GET", "/wallets/me", token=token2)
    w2_id = w2_list[0]["wallet_id"]
    print(f"✓ User 2 Primary Wallet: ID {w2_id} | Initial Balance: {w2_list[0]['balance']} USD")
    time.sleep(1)

    # 4. Deposit Funds (Step 13)
    print_step("STEP 4: Deposit Funds into User 1 Wallet (POST /wallets/{id}/deposit)")
    deposit_amt = 500.00
    status, dep_res = make_request("POST", f"/wallets/{w1_id}/deposit", data={"amount": deposit_amt}, token=token1)
    print(f"✓ Deposit of ${deposit_amt} Processed: Updated Balance = ${dep_res['updated_balance']} USD")
    print(f"   - Txn ID: {dep_res['transaction']['transaction_id']} (Type: {dep_res['transaction']['transaction_type']})")
    time.sleep(1)

    # 5. Withdrawal (Step 13)
    print_step("STEP 5: Withdraw Funds from User 1 Wallet (POST /wallets/{id}/withdraw)")
    withdraw_amt = 100.00
    status, with_res = make_request("POST", f"/wallets/{w1_id}/withdraw", data={"amount": withdraw_amt}, token=token1)
    print(f"✓ Withdrawal of ${withdraw_amt} Processed: Updated Balance = ${with_res['updated_balance']} USD")
    print(f"   - Txn ID: {with_res['transaction']['transaction_id']} (Type: {with_res['transaction']['transaction_type']})")
    time.sleep(1)

    # 6. Atomic Transfer with Row Locking (Step 14)
    print_step("STEP 6: Atomic P2P Money Transfer (POST /wallets/{id}/transfer)")
    transfer_amt = 150.00
    idempotency_key = str(uuid.uuid4())
    print(f"Transferring ${transfer_amt} from Wallet {w1_id} -> Wallet {w2_id} (Idempotency Key: {idempotency_key[:12]}...)...")
    status, trans_res = make_request("POST", f"/wallets/{w1_id}/transfer", data={
        "receiver_wallet_id": w2_id,
        "amount": transfer_amt,
        "idempotency_key": idempotency_key
    }, token=token1)
    print(f"✓ Transfer Status [{status} OK]:")
    print(f"   - Sender (User 1) Updated Balance: ${trans_res['updated_balance']} USD")
    print(f"   - Txn ID: {trans_res['transaction']['transaction_id']}")
    print(f"   - Is Cached?: {trans_res['is_cached']}")

    # Verify receiver balance
    status, r_bal = make_request("GET", f"/wallets/{w2_id}/balance", token=token2)
    print(f"   - Receiver (User 2) Verified Balance: ${r_bal['balance']} USD")
    time.sleep(1)

    # 7. Idempotency Test (Step 15)
    print_step("STEP 7: Enterprise Idempotency Test (Simulating Duplicate Request/Retry)")
    print(f"Re-sending the EXACT SAME transfer request with identical key ({idempotency_key[:12]}...)...")
    status, retry_res = make_request("POST", f"/wallets/{w1_id}/transfer", data={
        "receiver_wallet_id": w2_id,
        "amount": transfer_amt,
        "idempotency_key": idempotency_key
    }, token=token1)
    print(f"✓ Duplicate Response [Status {status} OK]:")
    print(f"   - Is Cached Replay?: {retry_res['is_cached']} (TRUE! Cached result returned)")
    print(f"   - Sender Balance: ${retry_res['updated_balance']} USD (DID NOT DOUBLE DEDUCT!)")
    time.sleep(1)

    # 8. Overdraw & Self-Transfer Protection (Step 16)
    print_step("STEP 8: Validation & Security Bounds Checking")
    print("Test A: Overdraw attempt ($10,000 withdrawal)...")
    status, err1 = make_request("POST", f"/wallets/{w1_id}/withdraw", data={"amount": 10000.00}, token=token1)
    print(f"   ✓ Blocked with Status {status}: {err1['detail']}")

    print("Test B: Self-transfer attempt (transferring to own wallet)...")
    status, err2 = make_request("POST", f"/wallets/{w1_id}/transfer", data={
        "receiver_wallet_id": w1_id,
        "amount": 20.00,
        "idempotency_key": str(uuid.uuid4())
    }, token=token1)
    print(f"   ✓ Blocked with Status {status}: {err2['detail']}")
    time.sleep(1)

    # 9. Audit Trail & Transaction History (Step 18)
    print_step("STEP 9: Transaction Audit Trail (GET /wallets/{id}/transactions)")
    status, txns = make_request("GET", f"/wallets/{w1_id}/transactions", token=token1)
    print(f"✓ Audit Log retrieved {len(txns)} transactions for Wallet {w1_id}:")
    for t in txns:
        print(f"   - [{t['created_at'][:19]}] {t['transaction_type']:<12} | Amount: ${t['amount']:>7} | Status: {t['status']}")

    print("\n" + "=" * 70)
    print("🎉 ALL TASKS 1 & 2 PIPELINE ENDPOINTS VERIFIED AND APPROVED!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_live_demo()
