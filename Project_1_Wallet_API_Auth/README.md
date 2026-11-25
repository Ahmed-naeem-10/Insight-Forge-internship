# 💳 GlobalPay Wallet API — Project 1: Setup, Database & Authentication

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Tests-9%2F9%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Project%201%20Complete-success.svg)]()

> Official submission for **Module 1: Project 1 (Setup, Database & Authentication)** of the Insight Forge Python Backend Development Internship.

---

## 📌 1. Project Overview & Description

GlobalPay Wallet is a fictional digital wallet fintech API designed to power web and mobile applications with secure user identity, multi-currency wallet management, and enterprise data models.

In **Project 1**, the foundation of the API was engineered:
- **Entity & Schema Modeling**: Designed relational schema across `users`, `wallets`, and `transactions` tables with strict constraints (`chk_balance_non_negative`, unique `idempotency_key`).
- **High-Volume Data Ingestion**: Extracted and seeded **60,773 records** (5,000 users, 5,773 wallets, 50,000 transactions) with verified foreign keys.
- **Authentication & Security**: Built user registration (`POST /auth/signup`) with automatic Primary wallet provisioning, industry-standard **bcrypt password hashing** (cost factor 12), and expiring **JSON Web Token (JWT)** issuance (`POST /auth/login`).
- **Protected Wallet Endpoints**: Built reusable `Depends(get_current_user)` authentication dependency enforcing access control on `GET /wallets/me` and `GET /wallets/{id}/balance`.

---

## 📸 2. Project Visual Showcase & Terminal Execution

### Interactive Swagger UI (`http://127.0.0.1:8000/docs`)
FastAPI auto-generates interactive OpenAPI documentation where all Project 1 endpoints can be tested live.

### Database Seeding Execution Log (`python scripts/seed_db.py`)
```text
==================================================
DATABASE SEEDING VERIFICATION SUMMARY
==================================================
Users Count:           5000 (Expected: 5,000)
Wallets Count:         5773 (Expected: 5,773)
Transactions Count:   50000 (Expected: 50,000)
==================================================
✓ All database rows successfully verified!
```

---

## 🛠️ 3. Tools & Technologies Used

| Category | Technology | Usage in Project 1 |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | Modern async REST API framework with automatic Swagger docs. |
| **Server** | **Uvicorn** | High-performance ASGI server for local development. |
| **ORM** | **SQLAlchemy 2.0** | Relational mapping for User, Wallet, and Transaction entities. |
| **Database** | **SQLite / PostgreSQL** | Local file-based SQLite database with PostgreSQL parity. |
| **Validation** | **Pydantic v2** | Request validation and response serialization (hiding password_hash). |
| **Security** | **Bcrypt & PyJWT** | Salted password hashing and signed HS256 access tokens. |
| **Testing** | **Pytest** | Automated unit and integration testing suite. |

---

## 📁 4. Project Architecture & File Structure

```text
project_1/
├── app/
│   ├── core/
│   │   ├── config.py         # App settings & environment variable loaders
│   │   ├── database.py       # Engine, sessionmaker & Base
│   │   ├── deps.py           # Reusable get_current_user JWT dependency
│   │   └── security.py       # Bcrypt hashing & PyJWT token utilities
│   ├── models/
│   │   ├── user.py           # SQLAlchemy User model (user_id, email, password_hash)
│   │   ├── wallet.py         # SQLAlchemy Wallet model (balance >= 0 constraint)
│   │   └── transaction.py    # SQLAlchemy Transaction model (UUID keys)
│   ├── schemas/
│   │   ├── user.py           # UserCreate, UserOut, LoginRequest, TokenResponse
│   │   ├── wallet.py         # WalletCreate, WalletOut, WalletBalanceOut
│   │   └── transaction.py    # Transaction schemas
│   ├── routers/
│   │   ├── auth.py           # /auth/signup, /auth/login, /auth/me
│   │   └── wallets.py        # /wallets/me, /wallets/{id}/balance, /wallets
│   └── main.py               # FastAPI entrypoint & router inclusion
├── scripts/
│   └── seed_db.py            # Bulk CSV database ingestion script
├── seed_data/                # Raw schema.sql and seed CSV datasets
├── tests/
│   ├── test_auth.py          # Authentication test suite
│   └── test_wallets.py       # Wallet authorization test suite
├── requirements.txt          # Pinned dependency manifest
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment variables template
├── TASK_1_REPORT.md          # Formal 1-2 page Task 1 report
└── README.md                 # Project 1 documentation
```

---

## ⚡ 5. Key Features & Results

1. **Clean Database Parity**:
   - `users`: **5,000 records** verified.
   - `wallets`: **5,773 records** verified.
   - `transactions`: **50,000 records** verified.
2. **Duplicate Account Defense**: Rejects duplicate registration attempts with `400 Bad Request`.
3. **Password Security**: `password_hash` is permanently hidden from all API response schemas.
4. **Access Control**: Attempting to view another customer's wallet balance is blocked with `403 Forbidden`.
5. **Auto Wallet Provisioning**: Every new user automatically receives a Primary USD wallet with balance `0.00`.

---

## 🧪 6. Automated Testing Suite

Execute the automated test suite:
```bash
pytest -v
```

### Execution Results:
```text
tests/test_auth.py::test_root_and_health PASSED                          [ 11%]
tests/test_auth.py::test_auth_signup_success PASSED                      [ 22%]
tests/test_auth.py::test_auth_signup_duplicate_email PASSED              [ 33%]
tests/test_auth.py::test_auth_login_success_and_token PASSED             [ 44%]
tests/test_auth.py::test_auth_login_invalid_password PASSED              [ 55%]
tests/test_wallets.py::test_wallets_unauthenticated PASSED               [ 66%]
tests/test_wallets.py::test_wallets_me_and_creation PASSED               [ 77%]
tests/test_wallets.py::test_wallet_unauthorized_access PASSED            [ 88%]
tests/test_wallets.py::test_wallet_not_found PASSED                      [100%]

============================== 9 passed in 5.68s ==============================
```

---

## 🚀 7. Quick Start Guide

### Step 1: Virtual Environment Setup
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Populate Database
```bash
python scripts/seed_db.py
```

### Step 4: Run API Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive docs will be available at: **http://127.0.0.1:8000/docs**

---

## 📄 8. Submission Deliverables
- [TASK_1_REPORT.md](TASK_1_REPORT.md) — Official 1–2 page written submission report.
- Complete source code in `app/`.
- Seed ingestion script in `scripts/seed_db.py`.
