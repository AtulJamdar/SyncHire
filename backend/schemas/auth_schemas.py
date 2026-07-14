import os
import re
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator

# Resolve common passwords path relative to this file
COMMON_PASSWORDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "common_passwords.txt"
)

try:
    with open(COMMON_PASSWORDS_PATH, "r", encoding="utf-8") as f:
        COMMON_PASSWORDS = set(line.strip().lower() for line in f if line.strip())
except Exception:
    COMMON_PASSWORDS = set()


def validate_password_complexity(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v) > 128:
        raise ValueError("Password must be under 128 characters")
    if not re.search(r"[a-zA-Z]", v):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"[0-9]", v):
        raise ValueError("Password must contain at least one number")
    if v.lower() in COMMON_PASSWORDS:
        raise ValueError("This password is too common — please choose a stronger one")
    return v


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_complexity(v)


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class ResetPasswordRequest(BaseModel):
    token: uuid.UUID
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_complexity(v)


class DeleteAccountRequest(BaseModel):
    confirm_email: EmailStr = Field(..., max_length=255)




