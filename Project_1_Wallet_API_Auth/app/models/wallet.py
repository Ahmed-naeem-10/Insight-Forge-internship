from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    currency = Column(String(10), nullable=False)
    balance = Column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    wallet_type = Column(String(20), nullable=False, default="Primary")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_balance_non_negative"),
    )

    # Relationships
    user = relationship("User", back_populates="wallets")
    sent_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_wallet_id",
        back_populates="sender_wallet",
    )
    received_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_wallet_id",
        back_populates="receiver_wallet",
    )

    def __repr__(self) -> str:
        return f"<Wallet id={self.wallet_id} user_id={self.user_id} currency={self.currency} balance={self.balance}>"

