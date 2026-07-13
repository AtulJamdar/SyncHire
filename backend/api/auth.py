import uuid
import logging
import sys
import os
from datetime import datetime, timedelta, timezone

# Add workspace root to sys.path to allow importing notifications
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


import time
import secrets
import httpx
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from config import settings
from core.database import get_db
from core.redis_client import redis
from core.security import hash_password, create_refresh_token, set_refresh_cookie, create_access_token, verify_password
from models.user import User, UserRole
from models.token import EmailVerificationToken, RefreshToken, PasswordResetToken
from schemas.auth_schemas import RegisterRequest, ResendVerificationRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from notifications.email.client import EmailClient
from middleware.auth_middleware import get_current_user

logger = logging.getLogger("auth_router")
email_client = EmailClient()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Check for existing email (verified or unverified)
    result = await db.execute(select(User).where(User.email == body.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_ALREADY_REGISTERED",
                "message": "Email is already registered"
            }
        )
        
    # 2. Hash password and create user
    hashed_pw = hash_password(body.password)
    new_user = User(
        name=body.name,
        email=body.email,
        password_hash=hashed_pw,
        role=UserRole.student,
        is_verified=False,
        is_active=True,
        is_deleted=False
    )
    db.add(new_user)
    await db.flush()  # populate new_user.id
    
    # 3. Generate verification token
    token_uuid = uuid.uuid4()
    token_record = EmailVerificationToken(
        user_id=new_user.id,
        token=token_uuid,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    db.add(token_record)
    await db.commit()
    
    # 4. Send verification email
    verification_url = f"{settings.NEXTAUTH_URL}/verify-email?token={token_uuid}"
    subject = "Verify your email address"
    html_body = f"""
    <p>Hi {body.name},</p>
    <p>Thank you for registering at Job Finder AI. Please verify your email address by clicking the link below:</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>This link will expire in 24 hours.</p>
    """
    
    try:
        email_sent = await email_client.send(
            to=body.email,
            subject=subject,
            html_body=html_body,
            from_name=settings.EMAIL_FROM_NAME,
            from_email=settings.EMAIL_FROM_ADDRESS
        )
        if not email_sent:
            logger.error(f"Failed to send verification email to {body.email}")
    except Exception as e:
        logger.error(f"Email service exception while sending to {body.email}: {e}")
        
    return { "message": "Verification email sent. Please check your inbox." }


@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(token: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # 1. Fetch verification token
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    
    # 2. Check token exists and has not been used
    if not token_record or token_record.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Verification token is invalid or has already been used"
            }
        )
        
    # 3. Check token expiration (older than 24 hours)
    now = datetime.now(timezone.utc)
    # Ensure token_record.expires_at is timezone-aware for correct comparison
    expires_at = token_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
        
    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Verification token has expired. Please request a new one."
            }
        )
        
    # 4. Fetch and verify user
    user_result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "User associated with this token was not found"
            }
        )
        
    user.is_verified = True
    
    # 5. Clean up verification token record
    await db.delete(token_record)
    await db.commit()
    return {
        "message": "Email verified successfully",
        "redirect": "/onboarding/step-1"
    }


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    body: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    email = body.email.strip().lower()
    
    # 1. Enforce rate limit: 3 requests / hour / email address using Redis
    rate_limit_key = f"rl:auth_resend:email:{email}"
    now = time.time()
    window_start = now - 3600
    
    try:
        pipe = redis.pipeline()
        pipe.zremrangebyscore(rate_limit_key, 0, window_start)  # Clean old requests
        pipe.zadd(rate_limit_key, {str(now): now})              # Add current request timestamp
        pipe.zcard(rate_limit_key)                              # Count total requests in window
        pipe.expire(rate_limit_key, 3601)                       # Expire key after 1 hour
        results = await pipe.execute()
        count = results[2]
        
        if count > 3:
            logger.warning(f"Email rate limit exceeded for {email} ({count}/3)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "TOO_MANY_REQUESTS",
                    "message": "Too many verification requests. Please try again later."
                }
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Redis email rate limiting connection failed: {e}")
        
    # Same standard response returned regardless of user existence or verification status
    success_response = {
        "message": "If an account exists with this email, a verification link has been sent."
    }

    # 2. Fetch user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # User doesn't exist → return success directly (prevents enumeration)
    if not user:
        return success_response
        
    # User is already verified → return success directly (prevents enumeration)
    if user.is_verified:
        return success_response
        
    # 3. Clean up any existing verification tokens for this user
    existing_tokens_result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id)
    )
    existing_tokens = existing_tokens_result.scalars().all()
    for token in existing_tokens:
        await db.delete(token)
        
    # 4. Generate new verification token
    token_uuid = uuid.uuid4()
    token_record = EmailVerificationToken(
        user_id=user.id,
        token=token_uuid,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    db.add(token_record)
    await db.commit()
    
    # 5. Send new verification email
    verification_url = f"{settings.NEXTAUTH_URL}/verify-email?token={token_uuid}"
    subject = "Verify your email address"
    html_body = f"""
    <p>Hi {user.name},</p>
    <p>A new email verification has been requested for your account. Please verify by clicking the link below:</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>This link will expire in 24 hours.</p>
    """
    
    try:
        email_sent = await email_client.send(
            to=user.email,
            subject=subject,
            html_body=html_body,
            from_name=settings.EMAIL_FROM_NAME,
            from_email=settings.EMAIL_FROM_ADDRESS
        )
        if not email_sent:
            logger.error(f"Failed to resend verification email to {user.email}")
    except Exception as e:
        logger.error(f"Email service exception while resending to {user.email}: {e}")
    return success_response


@router.get("/oauth/google")
async def oauth_google():
    # 1. Generate CSRF state token
    state = secrets.token_urlsafe(32)
    
    # 2. Save state server-side in Redis with 10-minute expiration
    state_key = f"oauth_state:{state}"
    try:
        await redis.set(state_key, "1", ex=600)
    except Exception as e:
        logger.error(f"Failed to save OAuth state to Redis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not initiate authentication. Please try again."
        )
        
    # 3. Construct Google authorization URL
    redirect_uri = f"{settings.NEXT_PUBLIC_API_URL}/api/auth/oauth/google/callback"
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "scope=openid%20email%20profile&"
        f"state={state}&"
        "access_type=offline&"
        "prompt=consent"
    )
    return RedirectResponse(auth_url)


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify CSRF state parameter
    state_key = f"oauth_state:{state}"
    try:
        stored_state = await redis.get(state_key)
        if not stored_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_STATE",
                    "message": "OAuth CSRF state mismatch or expired"
                }
            )
        await redis.delete(state_key)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Redis check failed during OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATE",
                "message": "Could not validate OAuth state. Please try again."
            }
        )

    # 2. Exchange authorization code for token
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = f"{settings.NEXT_PUBLIC_API_URL}/api/auth/oauth/google/callback"
    
    payload = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(token_url, data=payload)
            if token_response.status_code != 200:
                logger.error(f"Google token exchange failed: {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "code": "GOOGLE_API_UNAVAILABLE",
                        "message": "Google's token exchange endpoint returned an error"
                    }
                )
            tokens = token_response.json()
        except httpx.RequestError as e:
            logger.error(f"Google token endpoint unreachable: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GOOGLE_API_UNAVAILABLE",
                    "message": "Google OAuth endpoint is unreachable"
                }
            )
            
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GOOGLE_API_UNAVAILABLE",
                "message": "Access token not found in Google response"
            }
        )

    # 3. Retrieve user profile info from Google
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    async with httpx.AsyncClient() as client:
        try:
            userinfo_response = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if userinfo_response.status_code != 200:
                logger.error(f"Google userinfo retrieval failed: {userinfo_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "code": "GOOGLE_API_UNAVAILABLE",
                        "message": "Could not retrieve user info from Google"
                    }
                )
            user_info = userinfo_response.json()
        except httpx.RequestError as e:
            logger.error(f"Google userinfo endpoint unreachable: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GOOGLE_API_UNAVAILABLE",
                    "message": "Google userinfo endpoint is unreachable"
                }
            )

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GOOGLE_API_UNAVAILABLE",
                "message": "Required user information missing from Google profile"
            }
        )

    # 4. Create or link user account in database
    user_result = await db.execute(select(User).where(User.google_id == google_id))
    user = user_result.scalar_one_or_none()
    is_new_user = False

    if user:
        if not user.is_active or user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated or deleted"
            )
    else:
        # Check if a user with this email already exists
        email_result = await db.execute(select(User).where(User.email == email))
        user = email_result.scalar_one_or_none()
        
        if user:
            if not user.is_active or user.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated or deleted"
                )
            # Link existing account to Google
            user.google_id = google_id
            if not user.profile_picture_url:
                user.profile_picture_url = picture
            user.is_verified = True
        else:
            # Create new user
            user = User(
                name=name,
                email=email,
                google_id=google_id,
                profile_picture_url=picture,
                role=UserRole.student,
                is_verified=True,
                is_active=True,
                is_deleted=False
            )
            db.add(user)
            is_new_user = True
            
        await db.flush()

    # 5. Issue refresh token
    raw_refresh, hashed_refresh = create_refresh_token()
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(db_token)
    await db.commit()

    # 6. Redirect to frontend with refresh token cookie
    redirect_url = (
        f"{settings.NEXTAUTH_URL}/onboarding/step-1"
        if is_new_user
        else f"{settings.NEXTAUTH_URL}/dashboard"
    )
    
    response = RedirectResponse(url=redirect_url)
    set_refresh_cookie(response, raw_refresh)
    return response


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    email = body.email.strip().lower()
    
    # 1. Lockout check
    lockout_key = f"login_attempts:{email}"
    try:
        attempts_str = await redis.get(lockout_key)
        if attempts_str and int(attempts_str) >= 10:
            remaining = await redis.ttl(lockout_key)
            remaining = max(1, remaining)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "TOO_MANY_REQUESTS",
                    "message": f"Account temporarily locked due to too many failed attempts. Try again in {remaining // 60} minutes."
                },
                headers={"Retry-After": str(remaining)}
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Redis lockout check failed: {e}")

    # 2. Retrieve user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # Dummy hash for timing-safe verify_password
    dummy_hash = "$2b$12$LKnJ9n5L5L5L5L5L5L5L5OxU8v0lC6iLd7zWp8N/Q2Q2Q2Q2Q2Q2"
    
    if not user:
        # Dummy verification (takes standard bcrypt verify time)
        verify_password(body.password, dummy_hash)
        
        # Track failure attempt to prevent brute-force probing of email existence
        try:
            attempts = await redis.incr(lockout_key)
            if attempts == 1 or await redis.ttl(lockout_key) == -1:
                await redis.expire(lockout_key, 900)
        except Exception as e:
            logger.error(f"Redis increment failed: {e}")
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Wrong email or password"
            }
        )

    # 3. Verify password (Google OAuth users don't have password_hash)
    pw_hash = user.password_hash or dummy_hash
    is_valid_pw = verify_password(body.password, pw_hash) if user.password_hash else False
    
    if not is_valid_pw:
        try:
            attempts = await redis.incr(lockout_key)
            if attempts == 1 or await redis.ttl(lockout_key) == -1:
                await redis.expire(lockout_key, 900)
        except Exception as e:
            logger.error(f"Redis increment failed: {e}")
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Wrong email or password"
            }
        )

    # 4. Clear failures in Redis on success
    try:
        await redis.delete(lockout_key)
    except Exception as e:
        logger.error(f"Redis delete failed: {e}")

    # 5. Check if verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_NOT_VERIFIED",
                "message": "Email/password account is not yet verified"
            }
        )

    # 6. Check if active/suspended
    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_SUSPENDED",
                "message": "This account has been suspended"
            }
        )

    # 7. Issue access token
    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value
    )

    # 8. Issue refresh token
    raw_refresh, hashed_refresh = create_refresh_token()
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(db_token)
    await db.commit()

    # 9. Return JSON payload
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
    }
    
    # 10. Set refresh token HttpOnly cookie
    set_refresh_cookie(response, raw_refresh)
    return response_data


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # 1. Read refresh token from cookie
    raw_refresh = request.cookies.get("refresh_token")
    if not raw_refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Refresh token is missing"
            }
        )

    # 2. Hash and query the refresh token record
    token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid refresh token"
            }
        )

    # 3. Token Reuse Detection
    if record.revoked_at is not None:
        logger.warning(
            f"Token reuse detected for token_hash={token_hash[:10]}... "
            f"Revoking all active refresh tokens for user_id={record.user_id}."
        )
        # Revoke all sessions/tokens for this user as a precaution
        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == record.user_id)
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid refresh token"
            }
        )

    # 4. Check expiration
    now = datetime.now(timezone.utc)
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        await db.delete(record)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Refresh token has expired"
            }
        )

    # 5. Fetch associated user profile
    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active or user.is_deleted:
        await db.delete(record)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Associated user account is inactive or deleted"
            }
        )

    # 6. Rotate: mark current token as revoked/rotated
    record.revoked_at = now

    # 7. Issue new refresh token
    new_raw_refresh, new_hashed_refresh = create_refresh_token()
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hashed_refresh,
        expires_at=now + timedelta(days=7)
    )
    db.add(new_db_token)
    await db.commit()

    # 8. Issue new short-lived access token
    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role.value
    )

    # 9. Set the rotated refresh token in the response cookie
    set_refresh_cookie(response, new_raw_refresh)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 900
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Read refresh token from cookie
    raw_refresh = request.cookies.get("refresh_token")
    if raw_refresh:
        # 2. Hash and delete matching database record if it belongs to current_user
        token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        await db.execute(
            delete(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == current_user.id
            )
        )
        await db.commit()

    # 3. Clear cookie from client browser
    response.delete_cookie(key="refresh_token", path="/api/auth")
    
    return { "message": "Logged out successfully" }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    email = body.email.strip().lower()

    # 1. Enforce rate limit: 3 requests / hour / email address using Redis
    rate_limit_key = f"rl:auth_forgot:email:{email}"
    now = time.time()
    window_start = now - 3600
    
    try:
        pipe = redis.pipeline()
        pipe.zremrangebyscore(rate_limit_key, 0, window_start)  # Clean old requests
        pipe.zadd(rate_limit_key, {str(now): now})              # Add current request timestamp
        pipe.zcard(rate_limit_key)                              # Count total requests in window
        pipe.expire(rate_limit_key, 3601)                       # Expire key after 1 hour
        results = await pipe.execute()
        count = results[2]
        
        if count > 3:
            logger.warning(f"Forgot password rate limit exceeded for {email} ({count}/3)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "TOO_MANY_REQUESTS",
                    "message": "Too many password reset requests. Please try again later."
                }
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Redis email rate limiting connection failed: {e}")

    # Standard generic response
    generic_response = {
        "message": "If an account exists with this email, a reset link has been sent."
    }

    # 2. Fetch user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # User does not exist, or user is not active or user is deleted -> return 200 (no email enumeration)
    if not user or not user.is_active or user.is_deleted:
        return generic_response

    # 3. Clean up any existing password reset tokens for this user
    await db.execute(
        delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    )

    # 4. Generate new reset token
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(token_record)
    await db.commit()

    # 5. Send password reset email
    reset_url = f"{settings.NEXTAUTH_URL}/reset-password?token={raw_token}"
    subject = "Reset your password"
    html_body = f"""
    <p>Hi {user.name},</p>
    <p>We received a request to reset your password for your Job Finder AI account. Please click the link below to reset your password:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you did not request a password reset, you can safely ignore this email.</p>
    """

    try:
        email_sent = await email_client.send(
            to=user.email,
            subject=subject,
            html_body=html_body,
            from_name=settings.EMAIL_FROM_NAME,
            from_email=settings.EMAIL_FROM_ADDRESS
        )
        if not email_sent:
            logger.error(f"Failed to send password reset email to {user.email}")
    except Exception as e:
        logger.error(f"Email service exception while sending password reset to {user.email}: {e}")

    return generic_response


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Compute SHA-256 hash of the token
    token_hash = hashlib.sha256(str(body.token).encode()).hexdigest()

    # 2. Query PasswordResetToken record
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    if not record or record.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Reset token is invalid or has already been used"
            }
        )

    # 3. Check expiration (token older than 1 hour)
    now = datetime.now(timezone.utc)
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        await db.delete(record)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Reset token has expired. Please request a new one."
            }
        )

    # 4. Fetch user
    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "User associated with this token is invalid or suspended"
            }
        )

    # 5. Update user password hash, set verified = True
    user.password_hash = hash_password(body.new_password)
    user.is_verified = True

    # 6. Revoke all refresh tokens for the user (forces re-login on all devices)
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user.id)
    )

    # 7. Delete/Clean up the reset token
    await db.delete(record)
    await db.commit()

    return {
        "message": "Password reset successfully. Please log in with your new password."
    }







