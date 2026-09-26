# Password Encryption Module
# Uses Fernet (symmetric encryption) to securely encrypt/decrypt stored passwords.
# NOTE: This module handles ENCRYPTION (reversible), NOT password hashing (irreversible).
# The encryption key must be stored securely in environment variables.

from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()


def generate_key():
    """
    Generate a new Fernet encryption key.
    Run this once manually and store the key in .env as FERNET_KEY.
    WARNING: Never regenerate this key after storing encrypted data, as all previously
    encrypted passwords will become unrecoverable.
    """
    key = Fernet.generate_key().decode()
    return key


def get_fernet():
    """
    Load the encryption key from environment and initialize Fernet cipher.
    This is called by encrypt/decrypt functions to perform cryptographic operations.
    """
    key = os.getenv("FERNET_KEY")
    return Fernet(key.encode())


def encrypt_password(plain_text: str) -> str:
    """
    Encrypt a plain text password using Fernet symmetric encryption.
    Returns the encrypted password as a string for database storage.
    
    Args:
        plain_text: The unencrypted password
    
    Returns:
        Encrypted password string (base64-encoded for storage)
    """
    f = get_fernet()
    encrypted = f.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_password(encrypted_text: str) -> str:
    """
    Decrypt an encrypted password back to plain text.
    Only call this when displaying passwords to the user (requires authentication).
    
    Args:
        encrypted_text: The encrypted password from database
    
    Returns:
        Decrypted plain text password
    """
    f = get_fernet()
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()