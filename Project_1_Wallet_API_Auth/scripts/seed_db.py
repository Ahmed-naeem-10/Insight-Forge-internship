import os
import sys
import csv
from datetime import datetime
from decimal import Decimal

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction

SEED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed_data")


def parse_datetime(val: str):
    if not val or val.strip() == "":
        return datetime.utcnow()
    val = val.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass
    return datetime.utcnow()


def parse_optional_int(val: str):
    if not val or val.strip() == "":
        return None
    try:
        return int(float(val.strip()))
    except ValueError:
        return None


def seed_database():
    print("Initializing database schema...")
    # Create all tables according to SQLAlchemy models
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_users = db.query(User).count()
        if existing_users >= 5000:
            print(f"Database already contains {existing_users} users. Skipping seeding.")
            return

        print(f"Loading seed data from {SEED_DIR}...")

        # 1. Seed Users
        users_file = os.path.join(SEED_DIR, "seed_users.csv")
        users_batch = []
        with open(users_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                is_ver = str(row.get("is_verified", "")).strip().lower() in ("true", "1", "yes")
                users_batch.append({
                    "user_id": int(row["user_id"]),
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "phone_number": row.get("phone_number") or None,
                    "country": row["country"],
                    "password_hash": row["password_hash"],
                    "is_verified": is_ver,
                    "created_at": parse_datetime(row.get("created_at", "")),
                })

        print(f"Bulk inserting {len(users_batch)} users...")
        db.bulk_insert_mappings(User, users_batch)
        db.commit()

        # 2. Seed Wallets
        wallets_file = os.path.join(SEED_DIR, "seed_wallets.csv")
        wallets_batch = []
        with open(wallets_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                wallets_batch.append({
                    "wallet_id": int(row["wallet_id"]),
                    "user_id": int(row["user_id"]),
                    "currency": row["currency"],
                    "balance": Decimal(row["balance"]),
                    "wallet_type": row.get("wallet_type", "Primary"),
                    "created_at": parse_datetime(row.get("created_at", "")),
                })

        print(f"Bulk inserting {len(wallets_batch)} wallets...")
        db.bulk_insert_mappings(Wallet, wallets_batch)
        db.commit()

        # 3. Seed Transactions (in chunks for memory efficiency)
        txns_file = os.path.join(SEED_DIR, "seed_transactions.csv")
        txns_batch = []
        total_txns = 0
        with open(txns_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                txns_batch.append({
                    "transaction_id": row["transaction_id"],
                    "idempotency_key": row["idempotency_key"],
                    "sender_wallet_id": parse_optional_int(row.get("sender_wallet_id")),
                    "receiver_wallet_id": parse_optional_int(row.get("receiver_wallet_id")),
                    "transaction_type": row["transaction_type"],
                    "amount": Decimal(row["amount"]),
                    "status": row.get("status", "Completed"),
                    "created_at": parse_datetime(row.get("created_at", "")),
                })
                if len(txns_batch) >= 10000:
                    db.bulk_insert_mappings(Transaction, txns_batch)
                    db.commit()
                    total_txns += len(txns_batch)
                    print(f"Inserted {total_txns} transactions...")
                    txns_batch = []

            if txns_batch:
                db.bulk_insert_mappings(Transaction, txns_batch)
                db.commit()
                total_txns += len(txns_batch)
                print(f"Inserted {total_txns} transactions...")

        # 4. Verify Final Row Counts
        final_users = db.query(User).count()
        final_wallets = db.query(Wallet).count()
        final_txns = db.query(Transaction).count()

        print("\n" + "=" * 50)
        print("DATABASE SEEDING VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"Users Count:        {final_users:7d} (Expected: 5,000)")
        print(f"Wallets Count:      {final_wallets:7d} (Expected: 5,773)")
        print(f"Transactions Count: {final_txns:7d} (Expected: 50,000)")
        print("=" * 50)

        assert final_users == 5000, f"Expected 5000 users, got {final_users}"
        assert final_wallets == 5773, f"Expected 5773 wallets, got {final_wallets}"
        assert final_txns == 50000, f"Expected 50000 transactions, got {final_txns}"
        print("✓ All database rows successfully verified!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

