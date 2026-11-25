from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(36), primary_key=True)
    idempotency_key = Column(String(36), unique=True, nullable=False, index=True)
    sender_wallet_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable=True, index=True)
    receiver_wallet_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable=True, index=True)
    transaction_type = Column(String(30), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    status = Column(String(20), nullable=False, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_amount_positive"),
        Index("idx_txn_sender", "sender_wallet_id"),
        Index("idx_txn_receiver", "receiver_wallet_id"),
    )

    # Relationships
    sender_wallet = relationship(
        "Wallet",
        foreign_keys=[sender_wallet_id],
        back_populates="sent_transactions",
    )
    receiver_wallet = relationship(
        "Wallet",
        foreign_keys=[receiver_wallet_id],
        back_populates="received_transactions",
    )

    def __repr__(self) -> str:
        return f"<Transaction id={self.transaction_id} type={self.transaction_type} amount={self.amount} status={self.status}>"

