# 💳 GlobalPay Wallet API — Project 2: Transactions, Security & Deployment

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Postman](https://img.shields.io/badge/Postman-Collection%20Included-FF6C37.svg?logo=postman&logoColor=white)](https://www.postman.com/)
[![Tests](https://img.shields.io/badge/Tests-16%2F16%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Project%202%20Complete-success.svg)]()

> Official submission for **Module 1: Project 2 (Transactions, Security & Deployment)** of the Insight Forge Python Backend Development Internship.

---

## 📌 1. Project Overview & Description

In a production payments and digital wallet system, financial ledger operations must be strictly fault-tolerant. Money movement cannot be two separate operations; it must be an atomic transaction that never results in phantom debits, race conditions, or duplicate payments caused by mobile network retries.

Building upon the Project 1 foundation, **Project 2** delivers the complete transactional and deployment pipeline:
- **Deposit & Withdrawal (`POST /wallets/{id}/deposit`, `POST /wallets/{id}/withdraw`)**: Balance adjustments wrapped in database transactions preventing overdraws (`400 Bad Request`).
- **Atomic Peer-to-Peer Transfers (`POST /wallets/{id}/transfer`, `POST /wallets/transfer`)**:
  - Executes sender debit, receiver credit, and transaction record inside a single atomic database transaction (`BEGIN ... COMMIT`).
  - **Deadlock-Free Row-Level Locking**: Sorts wallet IDs in ascending order (`sorted([sender_id, receiver_id])`) and applies row locks (`with_for_update()`) to eliminate race conditions and double-spending.
- **Enterprise Idempotency**: Stripe/PayPal architecture model using client UUID `idempotency_key` ensuring duplicate requests return cached results (`is_cached: true`) without double-charging.
- **Security Hardening**: Integrated **SlowAPI** rate limiting (10 logins/min, 20 transfers/min), strict CORS, and structured Python logging.
- **Production Containerization**: Multi-service **Docker & Docker Compose** setup (FastAPI + PostgreSQL 16).

---

## 📸 2. Project Visual Showcase & Terminal Execution

### Real-Time Live Execution Showcase (`python scripts/live_demo.py`)
```text
======================================================================
  STEP 6: Atomic P2P Money Transfer (POST /wallets/{id}/transfer)
======================================================================
Transferring $150.0 from Wallet 5853 -> Wallet 5854 (Idempotency Key: ebb740ac...)...
✓ Transfer Status [200 OK]:
   - Sender (User 1) Updated Balance: $250.00 USD
   - Receiver (User 2) Verified Balance: $150.00 USD
   - Is Cached?: False

======================================================================
  STEP 7: Enterprise Idempotency Test (Simulating Duplicate Request/Retry)
======================================================================
Re-sending the EXACT SAME transfer request with identical key...
✓ Duplicate Response [Status 200 OK]:
   - Is Cached Replay?: True (Cached result returned!)
   - Sender Balance: $250.00 USD (DID NOT DOUBLE DEDUCT!)

======================================================================
  STEP 8: Validation & Security Bounds Checking
======================================================================
Test A: Overdraw attempt ($10,000 withdrawal)...
   ✓ Blocked with Status 400: Insufficient balance.
Test B: Self-transfer attempt (transferring to own wallet)...
   ✓ Blocked with Status 400: Cannot transfer funds to the same wallet.

======================================================================
  STEP 9: Transaction Audit Trail (GET /wallets/{id}/transactions)
======================================================================
✓ Audit Log retrieved 3 transactions for Wallet 5853:
   - [2026-11-21] Transfer     | Amount: $ 150.00 | Status: Completed
   - [2026-11-21] Withdrawal   | Amount: $ 100.00 | Status: Completed
   - [2026-11-21] Deposit      | Amount: $ 500.00 | Status: Completed
```

---

## 🛠️ 3. Tools & Technologies Used

| Category | Technology | Usage in Project 2 |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | REST API with dependency injection and OpenAPI /docs. |
| **ORM** | **SQLAlchemy 2.0** | Row locking (`with_for_update()`), atomic transactions, and relationships. |
| **Database** | **PostgreSQL 16 & SQLite** | Local testing on SQLite; multi-container Docker with PostgreSQL 16. |
| **Rate Limiter** | **SlowAPI** | IP-based request throttling against brute force and DDoS. |
| **Logging** | **Python `logging`** | Timestamped structured request logging (zero secret leakage). |
| **Testing** | **Pytest** | 16 unit and integration tests covering real edge cases. |
| **Containers** | **Docker & Docker Compose** | Multi-service orchestration with health checks. |
| **API Client** | **Postman** | Exported JSON collection with pre-configured requests and token scripts. |

---

## 📁 4. Project Architecture & File Organization

```text
project_2/
├── app/
│   ├── core/
│   │   ├── config.py         # Application settings & logging
│   │   ├── database.py       # Engine & session management
│   │   ├── deps.py           # Reusable get_current_user JWT dependency
│   │   ├── limiter.py        # SlowAPI rate limiter configuration
│   │   └── security.py       # Bcrypt hashing & PyJWT token utilities
│   ├── models/
│   │   ├── user.py           # SQLAlchemy User model
│   │   ├── wallet.py         # SQLAlchemy Wallet model
│   │   └── transaction.py    # SQLAlchemy Transaction model (UUID idempotency key)
│   ├── schemas/
│   │   ├── user.py           # User Pydantic schemas
│   │   ├── wallet.py         # Wallet Pydantic schemas
│   │   └── transaction.py    # Deposit, Withdraw, Transfer & Audit schemas
│   ├── routers/
│   │   ├── auth.py           # Authentication route handlers
│   │   └── wallets.py        # Wallet & money movement controllers
│   └── main.py               # FastAPI application setup, rate limiter, error handlers
├── scripts/
│   ├── seed_db.py            # High-performance bulk ingestion script (60,773 records)
│   └── live_demo.py          # Standalone end-to-end live testing demo script
├── seed_data/                # Raw schema.sql and seed CSV datasets
├── tests/
│   ├── conftest.py           # Pytest test fixtures
│   ├── test_auth.py          # Authentication tests
│   ├── test_wallets.py       # Wallet authorization tests
│   └── test_transactions.py  # Atomicity, idempotency, deposit, withdraw, transfer tests
├── Dockerfile                # Multi-stage production container definition
├── docker-compose.yml        # Orchestrates FastAPI service with PostgreSQL 16
├── GlobalPay_Wallet_API.postman_collection.json # Exported Postman collection
├── render.yaml & Procfile    # Cloud PaaS deployment specifications
├── requirements.txt          # Pinned dependency manifest
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment variables template
├── FINAL_PROJECT_REPORT.md   # Comprehensive Final Project Report (Tasks 1 & 2)
└── README.md                 # Project 2 documentation
```

---

## ⚡ 5. Key Features & Quality Benchmarks

1. **Transaction Atomicity**: Money movements are wrapped in `BEGIN ... COMMIT` blocks. Unhandled errors trigger immediate `ROLLBACK`.
2. **Deadlock Prevention**: Always acquires locks on wallet IDs in sorted ascending order.
3. **Idempotency Replay**: Replaying the same `idempotency_key` returns the cached transaction without moving balance twice.
4. **Rate Limiting**: Defends endpoints against spam with SlowAPI (`10/min` for login, `20/min` for transfers).
5. **Permanent Audit Trail**: All state changes are permanently logged to the `transactions` table.

---

## 🧪 6. Automated Testing Suite

Execute the automated test suite:
```bash
pytest -v
```

### Execution Results (16/16 Passing):
```text
tests/test_auth.py::test_root_and_health PASSED                          [  6%]
tests/test_auth.py::test_auth_signup_success PASSED                      [ 12%]
tests/test_auth.py::test_auth_signup_duplicate_email PASSED              [ 18%]
tests/test_auth.py::test_auth_login_success_and_token PASSED             [ 25%]
tests/test_auth.py::test_auth_login_invalid_password PASSED              [ 31%]
tests/test_transactions.py::test_deposit_and_withdrawal PASSED           [ 37%]
tests/test_transactions.py::test_atomic_transfer_success PASSED          [ 43%]
tests/test_transactions.py::test_transfer_insufficient_funds PASSED      [ 50%]
tests/test_transactions.py::test_transfer_to_self_rejected PASSED        [ 56%]
tests/test_transactions.py::test_transfer_currency_mismatch_rejected PASSED [ 62%]
tests/test_transactions.py::test_idempotency_key_replay_prevents_double_charge PASSED [ 68%]
tests/test_transactions.py::test_transaction_audit_trail_history PASSED  [ 75%]
tests/test_wallets.py::test_wallets_unauthenticated PASSED               [ 81%]
tests/test_wallets.py::test_wallets_me_and_creation PASSED               [ 87%]
tests/test_wallets.py::test_wallet_unauthorized_access PASSED            [ 93%]
tests/test_wallets.py::test_wallet_not_found PASSED                      [100%]

============================= 16 passed in 13.95s =============================
```

---

## 🚀 7. Quick Start & Execution

### Local Setup
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS

pip install -r requirements.txt
python scripts/seed_db.py
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Docker Deployment
```bash
docker-compose up --build
```
Interactive documentation: **http://127.0.0.1:8000/docs**

---

## 📄 8. Submission Deliverables
- [FINAL_PROJECT_REPORT.md](FINAL_PROJECT_REPORT.md) — Comprehensive technical report covering Tasks 1 & 2.
- [GlobalPay_Wallet_API.postman_collection.json](GlobalPay_Wallet_API.postman_collection.json) — Exported Postman collection.
- [docker-compose.yml](docker-compose.yml) & [Dockerfile](Dockerfile).
