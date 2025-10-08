"""Authentication schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "officer@example.com",
                "password": "SecurePassword123!"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class OTPSendRequest(BaseModel):
    """OTP send request schema."""
    email: str = Field(..., description="User email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "officer@example.com"
            }
        }


class OTPVerifyRequest(BaseModel):
    """OTP verify request schema."""
    email: str = Field(..., description="User email")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "officer@example.com",
                "otp_code": "123456"
            }
        }
