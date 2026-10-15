"""
Authentication API Router
Endpoints for login, registration, token refresh, password reset
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user, get_db
from app.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserInfo,
)
from app.api.schemas.responses import ApiResponse
from app.application.services.auth_service import get_auth_service

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Register a new user.

    **Public Endpoint** (No authentication required)

    **Business Rules:**
    - Email must be unique
    - Password must meet complexity requirements (min 8 chars, 1 uppercase, 1 number, 1 special char)
    - Default role: YOUTH_MEMBER
    - Email verification required before login

    **Request Body:**
    - name: Full name (2-100 characters)
    - email: Valid email address
    - password: Strong password
    - phone: Optional phone number (E.164 format)
    - branch_id: UUID of assigned branch

    **Returns:**
    - 201: Registration successful (check email for verification)
    - 400: Email already registered or validation error
    """
    result = await auth_service.register(payload, db)
    return ApiResponse(data=result)


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Authenticate user and issue access + refresh tokens.

    **Public Endpoint** (No authentication required)

    **Business Rules:**
    - User must exist and be active
    - Email must be verified (unless SUPER_ADMIN)
    - Password must match
    - Updates last_login_at timestamp
    - Refresh token stored in httpOnly cookie

    **Request Body:**
    - email: User email address
    - password: User password

    **Returns:**
    - 200: Login successful with tokens and user info
    - 401: Invalid credentials or email not verified

    **Response includes:**
    - access_token: JWT for API requests (15 min expiry)
    - refresh_token: JWT for token refresh (7 days expiry)
    - user: Complete user profile
    """
    login_response = await auth_service.login(payload, db)

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=login_response.refresh_token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/v1/auth",
    )

    return ApiResponse(data=login_response)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_tokens(
    payload: RefreshRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Refresh access token using refresh token.

    **Public Endpoint** (No authentication required)

    **Business Rules:**
    - Refresh token must be valid and not expired
    - User must still be active
    - Token rotation: new refresh token issued, old one invalidated

    **Request Body:**
    - refresh_token: Current refresh token

    **Returns:**
    - 200: New token pair issued
    - 401: Invalid or expired refresh token

    **Use Case:**
    Frontend detects access token expiry (401 error), calls this endpoint
    to get new tokens, then retries failed request.
    """
    tokens = await auth_service.refresh_tokens(payload.refresh_token, db)

    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return ApiResponse(data=TokenResponse(**tokens))


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Logout current user.

    **Protected Endpoint** (Authentication required)

    **Business Rules:**
    - Clears refresh token cookie
    - Frontend should clear access token from memory
    - TODO: Revoke refresh token in database

    **Returns:**
    - 200: Logout successful
    """
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    # TODO: Revoke refresh token in database

    return ApiResponse(data={"message": "Logout successful"})


@router.get("/me", response_model=ApiResponse[UserInfo])
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get current authenticated user profile.

    **Protected Endpoint** (Authentication required)

    **Returns:**
    - 200: User profile with complete information
    - 401: Not authenticated or token expired

    **Use Case:**
    Frontend calls this on app load to get user details and verify session.
    """
    return ApiResponse(data=UserInfo.model_validate(current_user))


@router.post("/verify-email", response_model=ApiResponse[dict])
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Verify user email with verification token.

    **Public Endpoint** (No authentication required)

    **Query Parameters:**
    - token: Email verification token from email link

    **Returns:**
    - 200: Email verified successfully
    - 400: Invalid or expired token

    **Use Case:**
    User clicks link in verification email, which redirects to frontend,
    frontend extracts token and calls this endpoint.
    """
    result = await auth_service.verify_email(token, db)
    return ApiResponse(data=result)


@router.post("/forgot-password", response_model=ApiResponse[dict])
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Request password reset email.

    **Public Endpoint** (No authentication required)

    **Request Body:**
    - email: User email address

    **Returns:**
    - 200: Always returns success (security - don't reveal if email exists)

    **Security Note:**
    Always returns success message regardless of whether email exists
    to prevent email enumeration attacks.
    """
    result = await auth_service.request_password_reset(payload.email, db)
    return ApiResponse(data=result)


@router.post("/reset-password", response_model=ApiResponse[dict])
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Reset password with reset token.

    **Public Endpoint** (No authentication required)

    **Request Body:**
    - token: Password reset token from email
    - new_password: New password (must meet complexity requirements)

    **Returns:**
    - 200: Password reset successful
    - 400: Invalid or expired token, or password validation failed

    **Side Effects:**
    - All existing refresh tokens are revoked (user must re-login on all devices)
    """
    result = await auth_service.reset_password(payload.token, payload.new_password, db)
    return ApiResponse(data=result)


@router.post("/resend-verification", response_model=ApiResponse[dict])
async def resend_verification_email(
    payload: ResendVerificationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    auth_service=Depends(get_auth_service),
):
    """
    Resend email verification link to current user.

    **Protected Endpoint** (Authentication required)

    **Business Rules:**
    - User must be authenticated
    - Email must not already be verified
    - Rate limiting applied (TODO: implement rate limiter middleware)

    **Returns:**
    - 200: Verification email sent successfully
    - 400: Email already verified
    - 401: Not authenticated

    **Use Case:**
    User didn't receive original verification email or it expired.
    Frontend provides "Resend Verification" button that calls this endpoint.

    **Rate Limiting:**
    TODO: Add rate limiting to prevent abuse (e.g., 3 requests per hour per user)
    """
    result = await auth_service.resend_verification_email(current_user.id, db)
    return ApiResponse(data=result)
