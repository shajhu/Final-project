"""
Encryption utility placeholder for future encrypted storage of intake and note data.

- Uses Fernet symmetric encryption from the cryptography package.
- Keys must never be committed to source control and should be stored in environment variables or a secure secret manager.
- This module is not yet integrated with persistent storage.
"""

from cryptography.fernet import Fernet

def generate_key() -> bytes:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()

def encrypt_text(text: str, key: bytes) -> bytes:
    """Encrypt text using the provided Fernet key."""
    f = Fernet(key)
    return f.encrypt(text.encode())

def decrypt_text(token: bytes, key: bytes) -> str:
    """Decrypt encrypted text using the provided Fernet key."""
    f = Fernet(key)
    return f.decrypt(token).decode()
