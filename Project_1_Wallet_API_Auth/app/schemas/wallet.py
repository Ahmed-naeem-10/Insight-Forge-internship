from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

SupportedCurrency = Literal["USD", "EUR", "GBP", "CAD", "AUD"]
SupportedWalletType = Literal["Primary", "Savings"]


class WalletBase(BaseModel):
    currency: SupportedCurrency = Field("USD", description="Wallet currency code")
    wallet_type: SupportedWalletType = Field("Savings", description="Type of wallet account")


class WalletCreate(WalletBase):
    pass


class WalletOut(BaseModel):
    wallet_id: int
    user_id: int
    currency: str
    balance: Decimal
    wallet_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletBalanceOut(BaseModel):
    wallet_id: int
    currency: str
    balance: Decimal
    wallet_type: str

    model_config = ConfigDict(from_attributes=True)

