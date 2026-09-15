"""
Unit tests for Core modules and Security logic.
Pruebas unitarias para módulos Core y lógica de seguridad.
"""

import pytest
from app.core.security import get_password_hash, verify_password

def test_password_hashing_and_verification() -> None:
    """
    Verify that password hashing and verification function correctly.
    Verifica que el hashing y verificación de contraseñas funcionen correctamente.
    """
    plain_password = "SecretPassword123!"
    hashed = get_password_hash(plain_password)
    
    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
