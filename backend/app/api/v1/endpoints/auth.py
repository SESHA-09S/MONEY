"""Authentication endpoints: register, login, token refresh, password management."""
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    service = UserService(db)
    existing = await service.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    schema = UserCreate(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
    )
    user = await service.create(schema)

    # Generate email verification token
    token = create_email_verification_token(user.email)
    user.email_verification_token = token
    # In production: background_tasks.add_task(send_verification_email, user.email, token)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and receive JWT tokens."""
    service = UserService(db)
    user = await service.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    # Update last login
    user.last_login = datetime.now(timezone.utc)

    access_token = create_access_token(
        subject=user.id,
        extra_data={"role": user.role.value, "email": user.email},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role.value,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a refresh token for a new access token."""
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    service = UserService(db)
    user = await service.get_by_id(int(data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(
        subject=user.id,
        extra_data={"role": user.role.value, "email": user.email},
    )
    new_refresh = create_refresh_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user_id=user.id,
        role=user.role.value,
    )


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify email address using the token sent to the user."""
    data = decode_token(payload.token)
    if not data or data.get("type") != "email_verify":
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    service = UserService(db)
    user = await service.get_by_email(data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_email_verified:
        return {"message": "Email already verified"}

    await service.set_email_verified(user)
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send password reset email."""
    service = UserService(db)
    user = await service.get_by_email(payload.email)
    # Always return 200 to prevent email enumeration
    if user:
        token = create_password_reset_token(user.email)
        user.password_reset_token = token
        # background_tasks.add_task(send_password_reset_email, user.email, token)
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using the token from email."""
    data = decode_token(payload.token)
    if not data or data.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    service = UserService(db)
    user = await service.get_by_email(data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await service.change_password(user, payload.new_password)
    user.password_reset_token = None
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password for authenticated user."""
    from app.core.security import verify_password
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    service = UserService(db)
    await service.change_password(current_user, payload.new_password)
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get currently authenticated user profile."""
    return current_user
