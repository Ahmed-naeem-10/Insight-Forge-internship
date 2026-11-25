from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="Full legal name of the user")
    email: str = Field(..., pattern=EMAIL_REGEX, description="Unique email address")
    phone_number: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    country: str = Field(..., min_length=2, max_length=50, description="Country of residence")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="Plaintext password to be hashed")


class UserOut(UserBase):
    user_id: int
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX, description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

