import pytest

from src.infrastructure.services.password_service import PasswordService


class TestPasswordService:
    """Tests for PasswordService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.password_service = PasswordService()

    def test_encrypt_returns_string(self):
        """Test that encrypt returns a string hash."""
        password = "SecurePassword123!"
        result = self.password_service.encrypt(password)

        assert isinstance(result, str)
        assert result != password
        assert result.startswith("$2b$")  # bcrypt hash prefix

    def test_encrypt_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = self.password_service.encrypt("password1")
        hash2 = self.password_service.encrypt("password2")

        assert hash1 != hash2

    def test_encrypt_same_password_produces_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "SecurePassword123!"
        hash1 = self.password_service.encrypt(password)
        hash2 = self.password_service.encrypt(password)

        # Due to bcrypt salting, same password should produce different hashes
        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Test that verify returns True for correct password."""
        password = "SecurePassword123!"
        hashed = self.password_service.encrypt(password)

        assert self.password_service.verify(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test that verify returns False for incorrect password."""
        password = "SecurePassword123!"
        hashed = self.password_service.encrypt(password)

        assert self.password_service.verify("WrongPassword!", hashed) is False

    def test_verify_empty_password(self):
        """Test verification with empty password."""
        password = "SecurePassword123!"
        hashed = self.password_service.encrypt(password)

        assert self.password_service.verify("", hashed) is False
