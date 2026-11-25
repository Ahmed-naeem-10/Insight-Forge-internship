-- ============================================================
-- Digital Wallet Backend API — Database Schema
-- Matches the seed data in wallet_api_seed_data.xlsx / seed_*.csv
-- Works on PostgreSQL. For SQLite, drop the SERIAL/BOOLEAN specifics
-- and use INTEGER PRIMARY KEY AUTOINCREMENT instead.
-- ============================================================

-- ============ USERS ============
CREATE TABLE users (
    user_id         SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    phone_number    VARCHAR(30),
    country         VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,   -- store bcrypt hash here, never plaintext
    is_verified     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============ WALLETS ============
CREATE TABLE wallets (
    wallet_id       SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    currency        VARCHAR(10) NOT NULL,             -- USD, GBP, CAD, AUD, EUR
    balance         NUMERIC(14,2) NOT NULL DEFAULT 0,  -- never let this go negative in app logic
    wallet_type     VARCHAR(20) NOT NULL DEFAULT 'Primary',  -- Primary / Savings
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_balance_non_negative CHECK (balance >= 0)
);

-- ============ TRANSACTIONS ============
CREATE TABLE transactions (
    transaction_id       UUID PRIMARY KEY,
    idempotency_key       UUID UNIQUE NOT NULL,   -- prevents duplicate processing of retried requests
    sender_wallet_id      INTEGER REFERENCES wallets(wallet_id),   -- NULL for Deposit (money from outside)
    receiver_wallet_id    INTEGER REFERENCES wallets(wallet_id),   -- NULL for Withdrawal (money to outside)
    transaction_type      VARCHAR(30) NOT NULL,   -- Transfer / Deposit / Withdrawal / Bill Payment / Merchant Payment
    amount                NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    status                VARCHAR(20) NOT NULL DEFAULT 'Pending',  -- Completed / Failed / Pending
    created_at            TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============ RECOMMENDED INDEXES ============
-- Speeds up "get all transactions for a wallet" — a very common API query
CREATE INDEX idx_txn_sender ON transactions(sender_wallet_id);
CREATE INDEX idx_txn_receiver ON transactions(receiver_wallet_id);
CREATE INDEX idx_wallets_user ON wallets(user_id);

-- ============ NOTES FOR STUDENTS ============
-- 1. sender_wallet_id and receiver_wallet_id are both nullable because:
--      - a Deposit has no sender (money enters from a bank/card outside the system)
--      - a Withdrawal has no receiver (money leaves to a bank/ATM outside the system)
-- 2. idempotency_key is UNIQUE — your API should reject a second request
--    with the same key instead of processing the transaction twice.
-- 3. The balance CHECK constraint is a safety net, not a substitute for
--    doing the debit/credit inside a single DB transaction (BEGIN...COMMIT).
