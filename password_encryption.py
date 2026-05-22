from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()


def generate_key():
    """We run this functions once and is used to generate encryption key"""
    key = Fernet.generate_key().decode()
    return key


def get_fernet():
    key = os.getenv("FERNET_KEY")
    return Fernet(key.encode())


def encrypt_password(plain_text: str) -> str:
    f = get_fernet()
    encrypted = f.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_password(encrypted_text: str) -> str:
    f = get_fernet()
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()