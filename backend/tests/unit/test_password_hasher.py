"""
Unit tests for password hashing service.

Tests password hashing, verification, and validation logic following
enterprise security standards.
"""

import pytest

from app.infrastructure.security.password_hasher import (
    PasswordHasher,
    PasswordValidationError,
    get_password_hasher,
)


class TestPasswordHasher:
    """Test suite for PasswordHasher class."""

    def setup_method(self):
        """Initialize hasher before each test."""
        self.hasher = PasswordHasher()

    # ─── Hash Password Tests ───────────────────────────────────────────────

    def test_hash_password_success(self):
        """Test successful password hashing."""
        plain = "SecurePass123!"
        hashed = self.hasher.hash_password(plain)

        # Verify hash is a string
        assert isinstance(hashed, str)
        # Verify bcrypt hash format (60 characters)
        assert len(hashed) == 60
        # Verify hash starts with bcrypt prefix
        assert hashed.startswith("$2b$")

    def test_hash_password_different_each_time(self):
        """Test that hashing same password produces different hashes (salt)."""
        plain = "SecurePass123!"
        hash1 = self.hasher.hash_password(plain)
        hash2 = self.hasher.hash_password(plain)

        # Different hashes due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert self.hasher.verify_password(plain, hash1)
        assert self.hasher.verify_password(plain, hash2)

    def test_hash_password_with_unicode(self):
        """Test password hashing with unicode characters."""
        # Password with unicode but meeting ASCII validation requirements
        plain = "Pässwörd123!"
        hashed = self.hasher.hash_password(plain)

        assert len(hashed) == 60
        assert self.hasher.verify_password(plain, hashed)

    def test_hash_password_empty_string_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            self.hasher.hash_password("")

    def test_hash_password_whitespace_only_raises_error(self):
        """Test that whitespace-only password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            self.hasher.hash_password("   ")

    def test_hash_password_non_string_raises_error(self):
        """Test that non-string password raises ValueError."""
        with pytest.raises(ValueError, match="Password must be a string"):
            self.hasher.hash_password(12345)  # type: ignore

    def test_hash_password_none_raises_error(self):
        """Test that None password raises ValueError."""
        with pytest.raises(ValueError, match="Password must be a string"):
            self.hasher.hash_password(None)  # type: ignore

    # ─── Verify Password Tests ─────────────────────────────────────────────

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        plain = "SecurePass123!"
        hashed = self.hasher.hash_password(plain)

        assert self.hasher.verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        plain = "SecurePass123!"
        hashed = self.hasher.hash_password(plain)

        assert self.hasher.verify_password("WrongPass123!", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        plain = "SecurePass123!"
        hashed = self.hasher.hash_password(plain)

        assert self.hasher.verify_password("securepass123!", hashed) is False
        assert self.hasher.verify_password("SECUREPASS123!", hashed) is False

    def test_verify_password_empty_plain_returns_false(self):
        """Test that empty plain password returns False."""
        hashed = self.hasher.hash_password("SecurePass123!")

        assert self.hasher.verify_password("", hashed) is False

    def test_verify_password_empty_hash_returns_false(self):
        """Test that empty hash returns False."""
        assert self.hasher.verify_password("SecurePass123!", "") is False

    def test_verify_password_invalid_hash_returns_false(self):
        """Test that invalid hash format returns False."""
        assert self.hasher.verify_password("SecurePass123!", "invalid_hash") is False

    def test_verify_password_non_string_plain_returns_false(self):
        """Test that non-string plain password returns False."""
        hashed = self.hasher.hash_password("SecurePass123!")

        assert self.hasher.verify_password(12345, hashed) is False  # type: ignore

    def test_verify_password_non_string_hash_returns_false(self):
        """Test that non-string hash returns False."""
        assert self.hasher.verify_password("SecurePass123!", 12345) is False  # type: ignore

    def test_verify_password_none_values_return_false(self):
        """Test that None values return False."""
        hashed = self.hasher.hash_password("SecurePass123!")

        assert self.hasher.verify_password(None, hashed) is False  # type: ignore
        assert self.hasher.verify_password("SecurePass123!", None) is False  # type: ignore

    # ─── Password Complexity Validation Tests ──────────────────────────────

    def test_validate_minimum_length(self):
        """Test password minimum length requirement (8 characters)."""
        with pytest.raises(
            PasswordValidationError,
            match="Password must be at least 8 characters long",
        ):
            self.hasher.hash_password("Short1!")

    def test_validate_requires_uppercase(self):
        """Test password requires at least one uppercase letter."""
        with pytest.raises(
            PasswordValidationError,
            match="Password must contain at least 1 uppercase letter",
        ):
            self.hasher.hash_password("lowercase123!")

    def test_validate_requires_number(self):
        """Test password requires at least one number."""
        with pytest.raises(
            PasswordValidationError, match="Password must contain at least 1 number"
        ):
            self.hasher.hash_password("NoNumbers!")

    def test_validate_requires_special_character(self):
        """Test password requires at least one special character."""
        with pytest.raises(
            PasswordValidationError,
            match="Password must contain at least 1 special character",
        ):
            self.hasher.hash_password("NoSpecial123")

    def test_validate_all_special_characters_accepted(self):
        """Test that all allowed special characters work."""
        special_chars = "!@#$%^&*"

        for char in special_chars:
            password = f"ValidPass1{char}"
            hashed = self.hasher.hash_password(password)
            assert self.hasher.verify_password(password, hashed)

    def test_validate_password_with_all_requirements(self):
        """Test valid password with all requirements."""
        valid_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Test1234!@#$",
            "Abcd1234!",
            "P@ssW0rd",
            "Testing123!",
            "C0mpl3x&Pass",
            "Str0ng^Passw0rd",
        ]

        for password in valid_passwords:
            hashed = self.hasher.hash_password(password)
            assert self.hasher.verify_password(password, hashed)

    def test_validate_edge_case_exactly_8_chars(self):
        """Test password with exactly 8 characters (minimum)."""
        password = "Pass123!"
        hashed = self.hasher.hash_password(password)
        assert self.hasher.verify_password(password, hashed)

    def test_validate_edge_case_long_password(self):
        """Test password with 72+ characters (bcrypt limit)."""
        # bcrypt has a 72-byte limit, but should still work
        password = "A1!" + "x" * 70
        hashed = self.hasher.hash_password(password)
        assert self.hasher.verify_password(password, hashed)

    # ─── Custom Rounds Tests ───────────────────────────────────────────────

    def test_custom_rounds(self):
        """Test hasher with custom bcrypt rounds."""
        hasher = PasswordHasher(rounds=10)
        password = "SecurePass123!"
        hashed = hasher.hash_password(password)

        # Should still hash and verify correctly
        assert hasher.verify_password(password, hashed)
        # Verify rounds in hash (format: $2b$10$...)
        assert hashed.startswith("$2b$10$")

    def test_default_rounds_is_12(self):
        """Test default bcrypt rounds is 12."""
        password = "SecurePass123!"
        hashed = self.hasher.hash_password(password)

        # Verify rounds in hash (format: $2b$12$...)
        assert hashed.startswith("$2b$12$")

    # ─── Singleton Instance Tests ──────────────────────────────────────────

    def test_get_password_hasher_returns_instance(self):
        """Test get_password_hasher returns PasswordHasher instance."""
        hasher = get_password_hasher()
        assert isinstance(hasher, PasswordHasher)

    def test_get_password_hasher_returns_same_instance(self):
        """Test get_password_hasher returns singleton instance."""
        hasher1 = get_password_hasher()
        hasher2 = get_password_hasher()

        assert hasher1 is hasher2

    def test_singleton_instance_works_correctly(self):
        """Test singleton instance hashes and verifies correctly."""
        hasher = get_password_hasher()
        password = "SecurePass123!"
        hashed = hasher.hash_password(password)

        assert hasher.verify_password(password, hashed)

    # ─── Security Property Tests ───────────────────────────────────────────

    def test_timing_attack_resistance(self):
        """
        Test that verify_password takes similar time for valid/invalid hashes.

        Note: This is a basic test. bcrypt's checkpw provides timing attack
        resistance internally through constant-time comparison.
        """
        import time

        password = "SecurePass123!"
        hashed = self.hasher.hash_password(password)

        # Time correct verification
        start = time.time()
        self.hasher.verify_password(password, hashed)
        correct_time = time.time() - start

        # Time incorrect verification
        start = time.time()
        self.hasher.verify_password("WrongPass123!", hashed)
        incorrect_time = time.time() - start

        # Both should take similar time (within order of magnitude)
        # This is a weak test but verifies basic timing resistance
        assert abs(correct_time - incorrect_time) < 0.5

    def test_hash_contains_salt(self):
        """Test that hash contains embedded salt (bcrypt property)."""
        password = "SecurePass123!"
        hash1 = self.hasher.hash_password(password)
        hash2 = self.hasher.hash_password(password)

        # Different hashes prove salt is embedded
        assert hash1 != hash2
        # Both hashes should work
        assert self.hasher.verify_password(password, hash1)
        assert self.hasher.verify_password(password, hash2)

    def test_rainbow_table_resistance(self):
        """
        Test resistance to rainbow table attacks through salt.

        Same password produces different hashes due to unique salt.
        """
        password = "CommonPassword123!"
        hashes = [self.hasher.hash_password(password) for _ in range(5)]

        # All hashes should be different
        assert len(set(hashes)) == 5
        # All hashes should verify
        for hashed in hashes:
            assert self.hasher.verify_password(password, hashed)


class TestPasswordValidationError:
    """Test suite for PasswordValidationError exception."""

    def test_password_validation_error_is_value_error(self):
        """Test PasswordValidationError inherits from ValueError."""
        error = PasswordValidationError("test")
        assert isinstance(error, ValueError)

    def test_password_validation_error_message(self):
        """Test PasswordValidationError preserves error message."""
        message = "Custom validation error"
        error = PasswordValidationError(message)
        assert str(error) == message


# ─── Integration-style Tests ───────────────────────────────────────────────


class TestPasswordHasherIntegration:
    """Integration-style tests for realistic usage scenarios."""

    def test_user_registration_flow(self):
        """Test typical user registration password flow."""
        hasher = PasswordHasher()

        # User submits password during registration
        user_password = "MySecure123!"

        # System hashes password
        hashed_password = hasher.hash_password(user_password)

        # Store hashed_password in database (simulated)
        stored_hash = hashed_password

        # Later, user tries to login
        login_password = "MySecure123!"

        # System verifies password
        is_valid = hasher.verify_password(login_password, stored_hash)
        assert is_valid is True

    def test_failed_login_attempt(self):
        """Test failed login with incorrect password."""
        hasher = PasswordHasher()

        # User registration
        correct_password = "MySecure123!"
        stored_hash = hasher.hash_password(correct_password)

        # User tries wrong password
        wrong_password = "WrongPass123!"
        is_valid = hasher.verify_password(wrong_password, stored_hash)
        assert is_valid is False

    def test_password_change_flow(self):
        """Test password change flow."""
        hasher = PasswordHasher()

        # Original password
        old_password = "OldPass123!"
        old_hash = hasher.hash_password(old_password)

        # User changes password
        new_password = "NewPass456!"
        new_hash = hasher.hash_password(new_password)

        # Old password should work with old hash
        assert hasher.verify_password(old_password, old_hash)
        # New password should work with new hash
        assert hasher.verify_password(new_password, new_hash)
        # Old password should NOT work with new hash
        assert not hasher.verify_password(old_password, new_hash)
        # New password should NOT work with old hash
        assert not hasher.verify_password(new_password, old_hash)

    def test_dependency_injection_pattern(self):
        """Test FastAPI dependency injection pattern."""
        # Simulate FastAPI dependency injection
        def endpoint(hasher: PasswordHasher = None):
            if hasher is None:
                hasher = get_password_hasher()
            return hasher

        # Get hasher through dependency
        hasher = endpoint()

        # Verify it works
        password = "TestPass123!"
        hashed = hasher.hash_password(password)
        assert hasher.verify_password(password, hashed)
