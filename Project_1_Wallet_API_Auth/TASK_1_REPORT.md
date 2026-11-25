# GlobalPay Wallet Backend API — Task 1 Report
**Python Backend Development Internship | Track: Backend Engineering**  
**Project Task 1 of 2: Setup, Database & Authentication**  
**Author / Engineer**: Internship Candidate  

---

## 1. API Design Summary

The objective of Task 1 was to establish the foundation of the GlobalPay Wallet backend: designing a clean API contract, structuring the codebase, configuring the persistence layer with 60,000+ seed records, and implementing secure user registration, token-based authentication, and authorized wallet operations.

### Planned vs. Implemented Endpoints
The final build matched all planned endpoints specified in the Step 1–12 requirements:

| Method | Endpoint | Auth Required | Description & Status |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | Operational status check for service monitoring. |
| `POST` | `/auth/signup` | No | Validates input, rejects duplicate emails, hashes password via bcrypt, persists User, and automatically provisions a Primary USD wallet. Returns `UserOut` (omits `password_hash`). |
| `POST` | `/auth/login` | No | Validates email & password hash; issues signed JWT access token with 60-minute expiration. |
| `GET` | `/auth/me` | Yes (`Bearer`) | Returns current authenticated user profile. |
| `GET` | `/wallets/me` | Yes (`Bearer`) | Returns all wallets belonging to the logged-in user extracted directly from JWT subject. |
| `GET` | `/wallets/{wallet_id}/balance`| Yes (`Bearer`) | Returns balance for the specified wallet, strictly enforcing ownership (`403 Forbidden` if attempting to view another user's wallet). |
| `POST` | `/wallets` | Yes (`Bearer`) | Creates an additional wallet (e.g. secondary currency or savings) for the logged-in user. |

---

## 2. Database Setup Notes

The database schema was implemented using SQLAlchemy ORM mirroring the provided `schema.sql` specification, providing seamless compatibility with SQLite for development and PostgreSQL for production.

### Entity Modeling & Constraints
1. **`users` Table**:
   - `user_id` (Primary Key, Autoincrement)
   - `email` (Unique Index, Not Null)
   - `password_hash` (Bcrypt hash storage, Not Null)
   - `is_verified` (Boolean flag)
2. **`wallets` Table**:
   - `wallet_id` (Primary Key, Autoincrement)
   - `user_id` (Foreign Key to `users.user_id` with `ON DELETE CASCADE`)
   - `currency` (USD, EUR, GBP, CAD, AUD)
   - `balance` (Numeric 14,2 with check constraint `balance >= 0`)
   - `wallet_type` (Primary / Savings)
3. **`transactions` Table**:
   - `transaction_id` (UUID Primary Key)
   - `idempotency_key` (UUID Unique Constraint to prevent replay attacks)
   - `sender_wallet_id` & `receiver_wallet_id` (Nullable Foreign Keys for Deposits/Withdrawals)
   - Performance Indexes: `idx_txn_sender`, `idx_txn_receiver`, `idx_wallets_user`

### Verified Seed Row Counts
Seed ingestion was executed via `scripts/seed_db.py`, utilizing chunked batch inserts for high memory efficiency. The row counts were verified against the seed dataset:

| Table | Target Count | Actual Seeded Count | Status |
| :--- | :---: | :---: | :---: |
| **`users`** | 5,000 | **5,000** | **VERIFIED** |
| **`wallets`** | ~5,773 | **5,773** | **VERIFIED** |
| **`transactions`** | 50,000 | **50,000** | **VERIFIED** |

---

## 3. Architecture Overview

The codebase is organized into layered, decoupled modules:

```text
[Client / Swagger UI]
         │ (HTTP / Bearer JWT)
         ▼
[FastAPI Application (app/main.py)]
         │
         ├── Middleware (CORS, Global Error Handlers)
         │
         ├── Routers (app/routers/auth.py, app/routers/wallets.py)
         │         │
         │         ├── Schemas (app/schemas/) — Request validation & Response serialization
         │         │
         │         └── Dependencies (app/core/deps.py) — JWT Bearer extraction & validation
         │
         ├── Security & Core (app/core/security.py, app/core/config.py) — Bcrypt & PyJWT
         │
         └── Persistence (app/models/, app/core/database.py) — SQLAlchemy ORM & SQLite/Postgres
```

### Request Flow
1. **Client Request**: Receives request at endpoint with optional `Authorization: Bearer <token>` header.
2. **Authentication Middleware / Dependency**: `Depends(get_current_user)` decodes and validates token signature, expiration (`exp`), and extracts user ID (`sub`).
3. **Pydantic Validation**: Request payload is parsed and validated against schema models before handler execution.
4. **Service / ORM Layer**: Interacts with database session (`SessionLocal`) via SQLAlchemy queries.
5. **Response Serialization**: ORM entities are converted through Pydantic response models, guaranteeing sensitive database fields (`password_hash`) are never leaked to clients.

---

## 4. Authentication Summary

### Security Choices & Implementations
- **Password Hashing**: 
  - Plaintext passwords are never logged or stored.
  - New user signups are hashed with industry-standard **bcrypt** with work factor cost (salt rounds = 12).
  - Seed users with pre-hashed SHA-256 signatures are also supported via dual-verification in `app/core/security.py`.
- **JWT Token Strategy**:
  - Tokens are signed using the `HS256` HMAC algorithm with a configurable secret key loaded from `.env`.
  - Claims include standard `sub` (subject user ID), `iat` (issued at), and `exp` (expiration timestamp).
  - Default token expiration is set to 60 minutes.
- **Route Protection**:
  - Protected endpoints require `HTTPBearer` authorization.
  - Calling protected routes without a token returns `401 Unauthorized`.
  - Attempting to inspect another user's wallet returns `403 Forbidden`.

---

## 5. Handoff Notes (Preparation for Task 2)

### What is Completed & Tested in Task 1:
- [x] Database schema deployed and 100% seeded (5,000 users, 5,773 wallets, 50,000 transactions).
- [x] `POST /auth/signup` and `POST /auth/login` working with bcrypt and JWT.
- [x] Automatic Primary wallet provisioning on signup.
- [x] Reusable authentication dependency `get_current_user`.
- [x] `GET /wallets/me`, `GET /wallets/{wallet_id}/balance`, and `POST /wallets` implemented with ownership security checks.
- [x] 100% test pass rate in automated test suite (`pytest -v`).
- [x] Interactive API documentation live at `/docs`.

### What Task 2 Will Build on Top of This Foundation:
1. **Deposit & Withdrawal Endpoints**: Implementing external funding into a user's wallet and debiting out to an external payment system.
2. **P2P Transfer Logic & Database Transactions**:
   - Atomic debit and credit operations within a single database transaction (`session.begin()`, commit/rollback).
   - Enforcing row locking (`with_for_update()`) to prevent race conditions and double-spending.
3. **Idempotency Handling**:
   - Utilizing the `idempotency_key` column on the `transactions` table to prevent duplicate transaction execution on network retries.
4. **Audit Logging & Transaction History**:
   - `GET /transactions` endpoint with filtering by wallet ID, date range, and status.

