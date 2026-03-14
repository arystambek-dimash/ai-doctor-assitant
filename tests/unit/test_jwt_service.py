import time

import jwt
import pytest

from src.infrastructure.services.jwt_service import JWTService


class TestJWTService:
    """Tests for JWTService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.access_secret = "test-access-secret-key-12345"
        self.refresh_secret = "test-refresh-secret-key-67890"
        self.jwt_service = JWTService(
            jwt_access_secret_key=self.access_secret,
            jwt_refresh_secret_key=self.refresh_secret,
        )

    def test_encode_access_token_returns_string(self):
        """Test that encode_access_token returns a valid JWT string."""
        payload = {"sub": "123", "email": "test@example.com"}
        token = self.jwt_service.encode_access_token(payload)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

    def test_encode_refresh_token_returns_string(self):
        """Test that encode_refresh_token returns a valid JWT string."""
        payload = {"sub": "123"}
        token = self.jwt_service.encode_refresh_token(payload)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_decode_access_token_returns_payload(self):
        """Test that decode_access_token returns the original payload."""
        original_payload = {"sub": "123", "email": "test@example.com"}
        token = self.jwt_service.encode_access_token(original_payload)
        decoded = self.jwt_service.decode_access_token(token)

        assert decoded["sub"] == original_payload["sub"]
        assert decoded["email"] == original_payload["email"]

    def test_decode_refresh_token_returns_payload(self):
        """Test that decode_refresh_token returns the original payload."""
        original_payload = {"sub": "456", "type": "refresh"}
        token = self.jwt_service.encode_refresh_token(original_payload)
        decoded = self.jwt_service.decode_refresh_token(token)

        assert decoded["sub"] == original_payload["sub"]
        assert decoded["type"] == original_payload["type"]

    def test_access_token_with_refresh_secret_fails(self):
        """Test that access token cannot be decoded with refresh secret."""
        payload = {"sub": "123"}
        access_token = self.jwt_service.encode_access_token(payload)

        with pytest.raises(jwt.InvalidSignatureError):
            self.jwt_service.decode_refresh_token(access_token)

    def test_refresh_token_with_access_secret_fails(self):
        """Test that refresh token cannot be decoded with access secret."""
        payload = {"sub": "123"}
        refresh_token = self.jwt_service.encode_refresh_token(payload)

        with pytest.raises(jwt.InvalidSignatureError):
            self.jwt_service.decode_access_token(refresh_token)

    def test_invalid_token_raises_exception(self):
        """Test that decoding invalid token raises exception."""
        with pytest.raises(jwt.DecodeError):
            self.jwt_service.decode_access_token("invalid.token.here")

    def test_tampered_token_raises_exception(self):
        """Test that decoding tampered token raises exception."""
        payload = {"sub": "123"}
        token = self.jwt_service.encode_access_token(payload)

        # Tamper with the token
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + "x" + "." + parts[2]

        with pytest.raises(jwt.DecodeError):
            self.jwt_service.decode_access_token(tampered)

    def test_expired_token_raises_exception(self):
        """Test that decoding expired token raises exception."""
        # Create a token that's already expired
        payload = {"sub": "123", "exp": int(time.time()) - 3600}  # 1 hour ago
        token = self.jwt_service.encode_access_token(payload)

        with pytest.raises(jwt.ExpiredSignatureError):
            self.jwt_service.decode_access_token(token)
