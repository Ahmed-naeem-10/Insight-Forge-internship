# GlobalPay Wallet Backend API — Final Project Report
**Python Backend Development Internship | Track: Backend Engineering**  
**Comprehensive Deliverable: Project Tasks 1 & 2 (Steps 1–24)**  
**Author / Engineer**: Internship Candidate  
**Date**: November 2026  

---

## 1. Executive Summary

GlobalPay Wallet is a production-grade, secure, and compliant digital wallet backend API engineered to power consumer-facing web and mobile financial applications. Built with FastAPI, SQLAlchemy ORM, and PostgreSQL/SQLite, the system enables users to create multi-currency accounts, securely hold funds, and execute peer-to-peer money movements. The single most important engineering decision in this project was the implementation of strict database transaction atomicity paired with UUID-based idempotency handling (the Stripe/PayPal architecture model), ensuring that money movements never result in phantom debits, double spending, or race conditions even under concurrent request loads or network retries.

---

## 2. API & Architecture Recap

### 2.1 Complete Endpoint Catalog

The backend exposes a fully RESTful, self-documenting interface divided into clean domain routers:

| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | System liveness probe returning service operational status. |
| `GET` | `/` | No | Root metadata endpoint pointing to interactive Swagger UI and ReDoc. |
| `POST` | `/auth/signup` | No | Registers user, hashes password via bcrypt, and auto-provisions a Primary USD wallet. |
| `POST` | `/auth/login` | No | Verifies credentials; issues signed JWT access token (Rate limited). |
| `GET` | `/auth/me` | Bearer | Fetches the current authenticated user profile. |
| `GET` | `/wallets/me` | Bearer | Retrieves all wallets owned by the logged-in user. |
| `GET` | `/wallets/{id}/balance` | Bearer | Retrieves balance for a specific wallet (strictly enforces ownership). |
| `POST` | `/wallets` | Bearer | Provisions a supplementary wallet (USD, EUR, GBP, CAD, AUD; Primary/Savings). |
| `POST` | `/wallets/{id}/deposit` | Bearer | Credits external funds into a wallet within an atomic database transaction. |
| `POST` | `/wallets/{id}/withdraw` | Bearer | Debits funds from a wallet, validating sufficient balance before withdrawal. |
| `POST` | `/wallets/{id}/transfer` | Bearer | Atomically transfers money to another wallet with row-level locking & idempotency. |
| `POST` | `/wallets/transfer` | Bearer | Direct transfer controller accepting explicit sender & receiver wallet IDs. |
| `GET` | `/wallets/{id}/transactions`| Bearer | Retrieves paginated chronological audit log of all transactions for a wallet. |

### 2.2 System Architecture & Project Layout

The repository follows a clean, modular structure separating business logic, data models, schemas, and routes:

```text
E:\projec3/
├── app/
│   ├── core/
│   │   ├── config.py         # Application settings, Pydantic BaseSettings & logging
│   │   ├── database.py       # SQLAlchemy engine, session maker & declarative Base
│   │   ├── deps.py           # Reusable get_current_user JWT dependency
│   │   ├── limiter.py        # SlowAPI rate limiter configuration
│   │   └── security.py       # Bcrypt hashing & PyJWT token utilities
│   ├── models/
│   │   ├── user.py           # SQLAlchemy User model (mapped to seed_users.csv)
│   │   ├── wallet.py         # SQLAlchemy Wallet model with check constraint balance >= 0
│   │   └── transaction.py    # SQLAlchemy Transaction model with UUID idempotency key
│   ├── schemas/
│   │   ├── user.py           # UserCreate, UserOut, LoginRequest, TokenResponse
│   │   ├── wallet.py         # WalletCreate, WalletOut, WalletBalanceOut
│   │   └── transaction.py    # DepositRequest, WithdrawRequest, TransferRequest, TransactionOut
│   ├── routers/
│   │   ├── auth.py           # Authentication route handlers
│   │   └── wallets.py        # Wallet & money movement controllers
│   └── main.py               # FastAPI application setup, CORS, rate limiter, error handlers
├── scripts/
│   ├── seed_db.py            # High-performance bulk ingestion script (60,773 records)
│   └── live_demo.py          # Standalone end-to-end live testing demo script
├── seed_data/                # Original schema.sql and seed CSV datasets
├── tests/
│   ├── conftest.py           # Pytest test environment fixtures
│   ├── test_auth.py          # Authentication test suite
│   ├── test_wallets.py       # Wallet authorization & creation tests
│   └── test_transactions.py  # Atomicity, idempotency, deposit, withdraw, transfer tests
├── Dockerfile                # Multi-stage production container definition
├── docker-compose.yml        # Orchestrates FastAPI service with PostgreSQL 16
├── GlobalPay_Wallet_API.postman_collection.json # Exported Postman collection
├── render.yaml & Procfile    # Cloud PaaS deployment specifications
├── requirements.txt          # Pinned Python package dependencies
├── .env.example              # Production environment variables template
└── README.md                 # Public documentation and quick-start guide
```

---

## 3. Transaction Design: Atomicity & Idempotency

### 3.1 The Atomicity Problem & Solution
A digital wallet transfer touches two distinct account rows simultaneously. If an application debits the sender's account and an unhandled exception or process termination occurs prior to crediting the receiver, money vanishes from the system. 

To eliminate this vulnerability:
1. **Single DB Transaction**: All operations (`sender debit -> receiver credit -> transaction audit log insert`) execute strictly inside a single database transaction block. Any exception automatically triggers `db.rollback()`.
2. **Deterministic Row Locking**: To prevent deadlocks when concurrent users transfer funds to each other simultaneously, wallets are locked in strictly ascending ID order (`sorted([sender_id, receiver_id])`) using `with_for_update()`.
3. **Double-Checked Balances**: The sender's balance is verified *after* acquiring the row-level lock, preventing race conditions where two simultaneous transactions read a stale balance.
4. **Safety Net Constraints**: The database table schema enforces `CHECK (balance >= 0)` on the database layer as a second line of defense.

### 3.2 Idempotency Architecture
In distributed financial networks, network timeouts and automatic client retries can cause duplicate transfers. 
- GlobalPay Wallet implements mandatory client-supplied `idempotency_key` (UUID v4) for all transfers.
- **Lookup Before Mutation**: Before debiting any funds, the system queries the `transactions` table for the incoming `idempotency_key`.
- **Cached Response Replay**: If the key exists, the API returns the original transaction record and current balance immediately, flagging `is_cached: true`. No balances are modified twice.
- **Unique Constraint**: The database column `idempotency_key` has a strict `UNIQUE` constraint, guaranteeing database-level protection against race conditions.

---

## 4. Security Measures & Hardening

1. **Bcrypt Password Hashing**: Passwords are never stored or logged in plaintext. Hashes are generated using bcrypt with salt rounds = 12. Pydantic response schemas (`UserOut`) explicitly exclude `password_hash`.
2. **Expiring JWT Tokens**: Authenticated sessions rely on HMAC-SHA256 (`HS256`) signed JSON Web Tokens containing subject user ID (`sub`), issue time (`iat`), and strict expiration (`exp`) set to 60 minutes.
3. **Rate Limiting**: Integrated `slowapi` to protect authentication and transaction routes against brute-force attacks and denial-of-service attempts:
   - Login: 10 requests / minute per client IP.
   - Signup: 15 requests / minute per client IP.
   - Transfers: 20 requests / minute per client IP.
4. **Strict Authorization & Information Barrier**: Endpoints enforce wallet ownership checks. If User A attempts to view or transfer from User B's wallet, the API returns `403 Forbidden` without revealing balance information.
5. **Secrets Hygiene**: All sensitive configuration (`DATABASE_URL`, `SECRET_KEY`) is externalized into `.env` loaded via `pydantic-settings`. `.env` is permanently excluded via `.gitignore`, while `.env.example` provides deployment guidance.

---

## 5. Testing Summary

Automated testing was executed via `pytest`, achieving **100% test pass rate (16/16 tests passing)**:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-8.3.5
collected 16 items

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

============================= 16 passed in 29.78s =============================
```

### Critical Edge Cases Verified:
- **Duplicate Registration**: Rejects duplicate email with `400 Bad Request`.
- **Negative & Zero Amounts**: Rejected with `422 Unprocessable Entity` via Pydantic validators.
- **Overdraw Protection**: Attempting to withdraw or transfer more than available balance triggers `400 Bad Request`.
- **Self-Transfer**: Transfers where `sender_wallet_id == receiver_wallet_id` are rejected with `400 Bad Request`.
- **Currency Mismatch**: Cross-currency transfers (e.g. USD to EUR) without explicit exchange rate conversion are rejected.
- **Idempotency Replay**: Re-sending identical transfer requests confirms zero duplicate deductions.

---

## 6. Deployment & Future Roadmap

### 6.1 Deployment Deliverables
- **Docker & Docker Compose**: Multi-container setup orchestrating the FastAPI application and PostgreSQL 16 database with health check definitions.
- **Render / Railway**: Preconfigured `render.yaml` and `Procfile` for cloud deployment.
- **Postman Collection**: Fully configured `GlobalPay_Wallet_API.postman_collection.json` with environment variables and automated token extraction.

### 6.2 Future Engineering Roadmap
Given additional development cycles, the following production enhancements are recommended:
1. **Refresh Token Flow**: Introduce short-lived access tokens (15 mins) paired with rotating refresh tokens stored in Redis.
2. **Automated Currency Conversion**: Integrate real-time FX rate providers to support multi-currency P2P transfers.
3. **Webhook Subscriptions**: Enable merchant webhooks dispatched upon transaction completion via asynchronous background queues (Celery/RabbitMQ).
4. **APM & Distributed Tracing**: Instrument OpenTelemetry and Prometheus metrics for end-to-end transaction latency monitoring.
