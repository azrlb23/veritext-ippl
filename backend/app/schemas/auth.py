from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = True


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    token_balance: int = 0
    ai_trial_remaining: int = 0
    ai_chat_allowance_remaining: int = 0

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: Optional[str] = None
    email: Optional[EmailStr] = None
    otp: Optional[str] = None
    new_password: str = Field(..., min_length=8, max_length=128)


class GoogleVerifyRequest(BaseModel):
    credential: str = Field(..., min_length=10)


class GoogleExchangeRequest(BaseModel):
    code: str = Field(..., min_length=10)


class GoogleCompleteRequest(BaseModel):
    ticket: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
