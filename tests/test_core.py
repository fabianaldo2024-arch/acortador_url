"""
Unit tests for core functionality and security.
Pruebas unitarias para la funcionalidad principal y seguridad.
"""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing() -> None:
    """Verify password hashing and verification / Verifica el hasheo de contraseñas."""
    password = "secret_password_123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_generation_and_decoding() -> None:
    """Verify JWT token encoding and decoding / Verifica generación y decodificación de JWT."""
    payload = {"sub": 1, "email": "user@example.com"}
    token = create_access_token(payload)
    
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "1"
    assert decoded["email"] == "user@example.com"
