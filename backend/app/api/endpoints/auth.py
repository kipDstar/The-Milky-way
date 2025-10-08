"""
Authentication endpoints.

Handles user login, token refresh, and OTP-based 2FA.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    generate_otp_code,
    hash_password,
)
from app.core.config import settings
from app.models.officer import Officer
from app.models.refresh_token import RefreshToken
from app.models.otp_code import OTPCode
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    OTPSendRequest,
    OTPVerifyRequest,
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token and refresh token.
    
    **Example:**
    ```json
    {
        "email": "officer@example.com",
        "password": "SecurePassword123!"
    }
    ```
    """
    # Find user by email
    user = db.query(Officer).filter(Officer.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Check if 2FA is enabled
    if user.two_factor_enabled:
        # For 2FA users, return a temporary token that requires OTP verification
        # In production, you might want to handle this differently
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Two-factor authentication required. Please verify OTP.",
            headers={"X-Requires-2FA": "true"}
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token_value = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        officer_id=user.id,
        token_hash=hash_token(refresh_token_value),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    **Example:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists and is valid
    token_hash_value = hash_token(refresh_data.refresh_token)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash_value,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalid or expired"
        )
    
    # Get user
    user = db.query(Officer).filter(Officer.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    # Optionally rotate refresh token (recommended for security)
    # For simplicity, we'll reuse the same refresh token
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/otp-send", status_code=status.HTTP_200_OK)
async def send_otp(
    otp_data: OTPSendRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP code via SMS for two-factor authentication.
    
    **Example:**
    ```json
    {
        "email": "officer@example.com"
    }
    ```
    """
    # Find user
    user = db.query(Officer).filter(Officer.email == otp_data.email).first()
    
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, an OTP has been sent."}
    
    if not user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled for this user"
        )
    
    # Generate OTP
    otp_code = generate_otp_code()
    
    # Store OTP in database (hashed)
    otp_record = OTPCode(
        officer_id=user.id,
        code_hash=hash_password(otp_code),  # Reuse password hashing
        expires_at=datetime.utcnow() + timedelta(minutes=10)  # 10 min expiry
    )
    db.add(otp_record)
    db.commit()
    
    # Send OTP via SMS (integrate with SMS service)
    # TODO: Integrate with SMS service
    # from app.services.sms import send_sms
    # await send_sms(user.phone, f"Your DDCPTS OTP code is: {otp_code}")
    
    # For development, log OTP (REMOVE IN PRODUCTION)
    if settings.is_development():
        print(f"OTP for {user.email}: {otp_code}")
    
    return {"message": "OTP sent successfully"}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    otp_data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and issue tokens.
    
    **Example:**
    ```json
    {
        "email": "officer@example.com",
        "otp_code": "123456"
    }
    ```
    """
    # Find user
    user = db.query(Officer).filter(Officer.email == otp_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Find valid OTP
    otp_records = db.query(OTPCode).filter(
        OTPCode.officer_id == user.id,
        OTPCode.is_used == False,
        OTPCode.expires_at > datetime.utcnow()
    ).order_by(OTPCode.created_at.desc()).all()
    
    valid_otp = None
    for otp_record in otp_records:
        if verify_password(otp_data.otp_code, otp_record.code_hash):
            valid_otp = otp_record
            break
    
    if not valid_otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    valid_otp.is_used = True
    valid_otp.used_at = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token_value = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        officer_id=user.id,
        token_hash=hash_token(refresh_token_value),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Logout by revoking refresh token.
    
    **Example:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    token_hash_value = hash_token(refresh_data.refresh_token)
    
    # Find and revoke token
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash_value
    ).first()
    
    if stored_token:
        stored_token.is_revoked = True
        stored_token.revoked_at = datetime.utcnow()
        db.commit()
    
    return {"message": "Logged out successfully"}
