"""
Password hashing and validation service using bcrypt.

This module provides secure password hashing with bcrypt (12 rounds) and
comprehensive password complexity validation following enterprise security standards.

Implements:
- FR-AUTH-002: Email Verification and Password Security
- FR-SEC-001: Password Security Standards
"""

import re
from typing import Final

import bcrypt


# Password complexity requirements
MIN_PASSWORD_LENGTH: Final[int] = 8
PASSWORD_PATTERN: Final[str] = r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])"
BCRYPT_ROUNDS: Final[int] = 12


class PasswordValidationError(ValueError):
    """Raised when password fails complexity validation."""

    pass


class PasswordHasher:
    """
    Service for secure password hashing and verification using bcrypt.

    This class provides methods to hash passwords with bcrypt (12 rounds) and
    verify passwords against stored hashes. It enforces password complexity
    requirements before hashing.

    Example:
        hasher = PasswordHasher()
        hashed = hasher.hash_password("SecurePass123!")
        is_valid = hasher.verify_password("SecurePass123!", hashed)
    """

    def __init__(self, rounds: int = BCRYPT_ROUNDS) -> None:
        """
        Initialize password hasher with specified bcrypt rounds.

        Args:
            rounds: Number of bcrypt rounds (default: 12). Higher values
                   increase security but also increase computation time.
        """
        self.rounds = rounds

    def hash_password(self, plain: str) -> str:
        """
        Hash a plain text password using bcrypt with 12 rounds.

        This method first validates the password against complexity requirements
        before hashing. The resulting hash is safe to store in the database.

        Args:
            plain: Plain text password to hash

        Returns:
            Bcrypt hash string (60 characters) safe for database storage

        Raises:
            PasswordValidationError: If password fails complexity validation
            ValueError: If plain password is not a string or is empty

        Example:
            >>> hasher = PasswordHasher()
            >>> hashed = hasher.hash_password("SecurePass123!")
            >>> len(hashed)
            60
        """
        # Input validation
        if not isinstance(plain, str):
            raise ValueError("Password must be a string")

        if not plain or not plain.strip():
            raise ValueError("Password cannot be empty")

        # Validate password complexity before hashing
        self._validate_password_complexity(plain)

        # Hash password with bcrypt
        password_bytes = plain.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)

        # Return as string for database storage
        return hashed_bytes.decode("utf-8")

    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verify a plain text password against a bcrypt hash.

        This method uses constant-time comparison to prevent timing attacks.
        It safely handles invalid hashes and returns False rather than raising
        exceptions for authentication flow compatibility.

        Args:
            plain: Plain text password to verify
            hashed: Bcrypt hash to verify against

        Returns:
            True if password matches hash, False otherwise

        Example:
            >>> hasher = PasswordHasher()
            >>> hashed = hasher.hash_password("SecurePass123!")
            >>> hasher.verify_password("SecurePass123!", hashed)
            True
            >>> hasher.verify_password("WrongPass123!", hashed)
            False
        """
        # Input validation - return False for invalid inputs rather than raising
        # This is safer for authentication flows
        if not isinstance(plain, str) or not isinstance(hashed, str):
            return False

        if not plain or not plain.strip() or not hashed or not hashed.strip():
            return False

        try:
            password_bytes = plain.encode("utf-8")
            hashed_bytes = hashed.encode("utf-8")

            # bcrypt.checkpw handles constant-time comparison
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError):
            # Invalid hash format or encoding error
            return False

    def _validate_password_complexity(self, password: str) -> None:
        """
        Validate password against complexity requirements.

        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 number
        - At least 1 special character (!@#$%^&*)

        Args:
            password: Password to validate

        Raises:
            PasswordValidationError: If password fails any requirement with
                                     specific error message
        """
        # Check minimum length
        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordValidationError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
            )

        # Check for uppercase letter
        if not re.search(r"[A-Z]", password):
            raise PasswordValidationError(
                "Password must contain at least 1 uppercase letter"
            )

        # Check for digit
        if not re.search(r"\d", password):
            raise PasswordValidationError("Password must contain at least 1 number")

        # Check for special character
        if not re.search(r"[!@#$%^&*]", password):
            raise PasswordValidationError(
                "Password must contain at least 1 special character (!@#$%^&*)"
            )


# Singleton instance for dependency injection
_password_hasher_instance: PasswordHasher | None = None


def get_password_hasher() -> PasswordHasher:
    """
    Get singleton instance of PasswordHasher for dependency injection.

    This function provides a singleton instance suitable for FastAPI
    dependency injection using Depends().

    Returns:
        Singleton PasswordHasher instance

    Example:
        from fastapi import Depends
        from app.infrastructure.security.password_hasher import (
            get_password_hasher, PasswordHasher
        )

        async def endpoint(hasher: PasswordHasher = Depends(get_password_hasher)):
            hashed = hasher.hash_password("password")
    """
    global _password_hasher_instance
    if _password_hasher_instance is None:
        _password_hasher_instance = PasswordHasher()
    return _password_hasher_instance
