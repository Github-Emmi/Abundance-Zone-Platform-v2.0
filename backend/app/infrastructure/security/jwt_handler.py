"""
JWT Token Handler Module
Handles JWT token creation, validation, and refresh token rotation
Implements: FR-AUTH-006, FR-AUTH-007
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import jwt, JWTError

from app.core.config import settings
from app.core.exceptions import InvalidTokenException, TokenExpiredException


class TokenPair:
    """Data class for access and refresh token pair"""

    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.token_type = "Bearer"


class JWTHandler:
    """
    JWT Token Handler for authentication

    Provides methods for:
    - Creating access tokens (15-minute expiry)
    - Creating refresh tokens (7-day expiry)
    - Creating token pairs (both access and refresh)
    - Verifying tokens with expiry validation
    - Decoding expired tokens (for password reset flows)

    Security Features:
    - HS256 algorithm
    - Unique JTI (JWT ID) for each token
    - Separate secrets for access and refresh tokens
    - Token expiry enforcement
    """

    ALGORITHM = "HS256"

    @staticmethod
    def create_access_token(payload: dict[str, Any]) -> str:
        """
        Generate access token with 15-minute expiry.

        Args:
            payload: Token payload containing user claims (sub, email, role, branch_id)

        Returns:
            Encoded JWT access token string

        Example:
            >>> token = JWTHandler.create_access_token({
            ...     "sub": "user-uuid",
            ...     "email": "user@example.com",
            ...     "role": "BRANCH_COORDINATOR",
            ...     "branch_id": "branch-uuid"
            ... })
        """
        data = payload.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        data.update(
            {
                "exp": expire,
                "iat": now,
                "jti": str(uuid4()),  # Unique token identifier
                "type": "access",
            }
        )

        return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=JWTHandler.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Generate refresh token with 7-day expiry.

        Args:
            user_id: User UUID to embed in token

        Returns:
            Encoded JWT refresh token string

        Example:
            >>> token = JWTHandler.create_refresh_token("user-uuid")
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "jti": str(uuid4()),  # Unique token identifier
            "type": "refresh",
        }

        return jwt.encode(
            payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=JWTHandler.ALGORITHM
        )

    @staticmethod
    def create_token_pair(payload: dict[str, Any]) -> TokenPair:
        """
        Generate both access and refresh tokens in one call.

        Used during login and token refresh flows to ensure atomic token generation.

        Args:
            payload: Token payload containing user claims (sub, email, role, branch_id)

        Returns:
            TokenPair object containing access_token, refresh_token, expires_in, token_type

        Example:
            >>> tokens = JWTHandler.create_token_pair({
            ...     "sub": "user-uuid",
            ...     "email": "user@example.com",
            ...     "role": "BRANCH_COORDINATOR",
            ...     "branch_id": "branch-uuid"
            ... })
            >>> print(tokens.access_token)
            >>> print(tokens.refresh_token)
            >>> print(tokens.expires_in)  # 900 (15 minutes in seconds)
        """
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Payload must contain 'sub' field with user ID")

        access_token = JWTHandler.create_access_token(payload)
        refresh_token = JWTHandler.create_refresh_token(user_id)
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    @staticmethod
    def verify_token(token: str, secret: str) -> dict[str, Any]:
        """
        Verify and decode JWT token with expiry validation.

        Args:
            token: JWT token string to verify
            secret: Secret key to verify token signature

        Returns:
            Decoded token payload as dictionary

        Raises:
            TokenExpiredException: If token has expired
            InvalidTokenException: If token signature is invalid or malformed

        Example:
            >>> payload = JWTHandler.verify_token(token, settings.JWT_SECRET_KEY)
            >>> user_id = payload["sub"]
        """
        try:
            payload = jwt.decode(token, secret, algorithms=[JWTHandler.ALGORITHM])

            # Verify expiry manually for better error messages
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                raise InvalidTokenException()

            expiry = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if expiry < datetime.now(timezone.utc):
                raise TokenExpiredException()

            return payload

        except JWTError as e:
            # Convert jose library errors to domain exceptions
            if "expired" in str(e).lower():
                raise TokenExpiredException()
            raise InvalidTokenException()

    @staticmethod
    def verify_refresh_token(token: str) -> dict[str, Any]:
        """
        Verify refresh token specifically using refresh secret.

        Convenience method that wraps verify_token with the refresh secret.
        Used in token refresh endpoint.

        Args:
            token: JWT refresh token string to verify

        Returns:
            Decoded token payload as dictionary

        Raises:
            TokenExpiredException: If token has expired
            InvalidTokenException: If token signature is invalid or malformed

        Example:
            >>> payload = JWTHandler.verify_refresh_token(refresh_token)
            >>> user_id = payload["sub"]
        """
        payload = JWTHandler.verify_token(token, settings.JWT_REFRESH_SECRET_KEY)

        # Verify it's actually a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":
            raise InvalidTokenException()

        return payload

    @staticmethod
    def decode_token_unsafe(token: str) -> dict[str, Any] | None:
        """
        Decode JWT token WITHOUT signature or expiry validation.

        SECURITY WARNING: This method does NOT verify token authenticity.
        Only use for:
        - Password reset flows (to extract email from expired tokens)
        - Token inspection/debugging
        - Extracting claims from tokens that may be expired

        Args:
            token: JWT token string to decode

        Returns:
            Decoded token payload as dictionary, or None if completely malformed

        Example:
            >>> # Extract email from expired password reset token
            >>> payload = JWTHandler.decode_token_unsafe(expired_token)
            >>> if payload:
            ...     email = payload.get("email")
        """
        try:
            # Decode without verification (options parameter disables all checks)
            # Note: jose library still requires a key parameter, but we use a dummy one
            # since signature verification is disabled
            payload = jwt.decode(
                token,
                key="",  # Dummy key (not used when verify_signature=False)
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
            return payload

        except JWTError:
            # Token is completely malformed (not even valid JWT structure)
            return None

    @staticmethod
    def extract_user_id_from_token(token: str) -> str | None:
        """
        Extract user ID from token without full verification.

        Convenience method for extracting the 'sub' claim from an unverified token.
        Useful for password reset flows.

        Args:
            token: JWT token string

        Returns:
            User ID string, or None if extraction fails

        Example:
            >>> user_id = JWTHandler.extract_user_id_from_token(token)
        """
        payload = JWTHandler.decode_token_unsafe(token)
        return payload.get("sub") if payload else None
