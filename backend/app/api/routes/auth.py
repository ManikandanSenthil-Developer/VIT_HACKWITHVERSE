from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.rate_limiter import rate_limit_dependency
from app.models.user import User
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.audit.audit_service import audit_service

router = APIRouter()


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency(max_requests=10, window_seconds=60, action="register"))],
)
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user account."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    existing_user = AuthService.get_by_email(db, email=user_in.email)
    if existing_user:
        audit_service.log_event(
            db=db,
            action="FAILED_REGISTER",
            details={"email": user_in.email, "reason": "already_exists"},
            ip_address=client_ip,
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    user = AuthService.register(db, user_in=user_in)
    audit_service.log_event(
        db=db,
        action="REGISTER",
        user_id=user.id,
        resource_type="User",
        resource_id=str(user.id),
        ip_address=client_ip,
        status="SUCCESS",
    )
    return AuthService.create_tokens_for_user(user)


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(rate_limit_dependency(max_requests=15, window_seconds=60, action="login"))],
)
def login(request: Request, user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    """Authenticate user with email and password."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user = AuthService.authenticate(db, email=user_in.email, password=user_in.password)
    if not user:
        audit_service.log_event(
            db=db,
            action="FAILED_LOGIN",
            details={"email": user_in.email},
            ip_address=client_ip,
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        audit_service.log_event(
            db=db,
            action="FAILED_LOGIN",
            user_id=user.id,
            details={"email": user_in.email, "reason": "inactive_account"},
            ip_address=client_ip,
            status="BLOCKED",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    audit_service.log_event(
        db=db,
        action="LOGIN",
        user_id=user.id,
        resource_type="User",
        resource_id=str(user.id),
        ip_address=client_ip,
        status="SUCCESS",
    )
    return AuthService.create_tokens_for_user(user)


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> Any:
    """Refresh access token using refresh token."""
    token = AuthService.refresh_access_token(db, refresh_token=request.refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
    """Get current authenticated user details."""
    return current_user
