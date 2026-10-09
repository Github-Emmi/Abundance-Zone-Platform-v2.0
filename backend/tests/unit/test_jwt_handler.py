"""JWT Handler Unit Tests"""
import pytest
from datetime import datetime, timedelta, timezone
from app.infrastructure.security.jwt_handler import JWTHandler, TokenPair
from app.core.exceptions import InvalidTokenException, TokenExpiredException


def test_create_access_token():
    """Test creating access token"""
    payload = {"sub": "user-123", "email": "test@test.com", "role": "SUPER_ADMIN"}
    token = JWTHandler.create_access_token(payload)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token():
    """Test creating refresh token"""
    token = JWTHandler.create_refresh_token("user-123")
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_token_pair():
    """Test creating token pair"""
    payload = {"sub": "user-123", "email": "test@test.com"}
    tokens = JWTHandler.create_token_pair(payload)
    
    assert isinstance(tokens, TokenPair)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.expires_in == 900  # 15 minutes in seconds
    assert tokens.token_type == "Bearer"


def test_verify_valid_token():
    """Test verifying a valid token"""
    from app.core.config import settings
    payload = {"sub": "user-123", "email": "test@test.com"}
    token = JWTHandler.create_access_token(payload)
    
    decoded = JWTHandler.verify_token(token, settings.JWT_SECRET_KEY)
    
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "test@test.com"
    assert decoded["type"] == "access"


def test_verify_refresh_token():
    """Test verifying refresh token"""
    from app.core.config import settings
    token = JWTHandler.create_refresh_token("user-123")
    
    decoded = JWTHandler.verify_refresh_token(token)
    
    assert decoded["sub"] == "user-123"
    assert decoded["type"] == "refresh"


def test_decode_token_unsafe():
    """Test decoding token without verification"""
    payload = {"sub": "user-123", "email": "test@test.com"}
    token = JWTHandler.create_access_token(payload)
    
    decoded = JWTHandler.decode_token_unsafe(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"


def test_extract_user_id_from_token():
    """Test extracting user ID from token"""
    payload = {"sub": "user-123"}
    token = JWTHandler.create_access_token(payload)
    
    user_id = JWTHandler.extract_user_id_from_token(token)
    
    assert user_id == "user-123"
