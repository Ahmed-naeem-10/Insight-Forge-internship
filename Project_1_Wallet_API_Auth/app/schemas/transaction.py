from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class DepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Deposit amount (must be positive)")
    idempotency_key: Optional[UUID] = Field(default_factory=uuid4, description="Optional idempotency key to prevent double deposit")


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Withdrawal amount (must be positive)")
    idempotency_key: Optional[UUID] = Field(default_factory=uuid4, description="Optional idempotency key to prevent double withdrawal")


class TransferRequest(BaseModel):
    receiver_wallet_id: int = Field(..., description="Destination receiver wallet ID")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Transfer amount (must be positive)")
    idempotency_key: UUID = Field(..., description="Unique client idempotency key to prevent double charging on network retry")


class DirectTransferRequest(BaseModel):
    sender_wallet_id: int = Field(..., description="Source sender wallet ID (must belong to authenticated user)")
    receiver_wallet_id: int = Field(..., description="Destination receiver wallet ID")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Transfer amount (must be positive)")
    idempotency_key: UUID = Field(..., description="Unique client idempotency key to prevent double charging")


class TransactionOut(BaseModel):
    transaction_id: str
    idempotency_key: str
    sender_wallet_id: Optional[int] = None
    receiver_wallet_id: Optional[int] = None
    transaction_type: str
    amount: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionDetailResponse(BaseModel):
    message: str
    transaction: TransactionOut
    updated_balance: Optional[Decimal] = None
    is_cached: bool = Field(False, description="True if result was returned from idempotent cache without re-processing")
