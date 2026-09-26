# Password Hashing Module
# Uses Argon2 (memory-hard hash function) for secure password storage.
# NOTE: This module handles HASHING (irreversible), NOT encryption (reversible).
# Hashed passwords are stored in the database and compared during login authentication.
# IMPORTANT: Never use plain passwords - always hash before storage!

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import time

# --- Argon2 Configuration ---
# PasswordHasher instance with security parameters tuned for password hashing
ph = PasswordHasher(
    time_cost=2,  # Number of passes over memory (iterations) - increase for slower hashing
    memory_cost=131072,  # Memory usage in KB (131072 KB = 128 MB) - increase for more resistance to GPU attacks
    parallelism=2,  # Number of threads used during hashing - increase for parallelization
    hash_len=32,  # Length of the final hash in bytes (256 bits)
    salt_len=16  # Length of random salt in bytes (128 bits) - ensures each hash is unique
)


# --- Hashing Function ---
def hash_password(plain_text: str) -> str:
    """
    Hash a plain text password using Argon2.
    
    The Argon2 hash includes:
    - Algorithm identifier
    - Parameters (time_cost, memory_cost, parallelism)
    - Random salt
    - Derived hash
    
    Store the entire returned string directly in the database - do NOT extract parts.
    This string is used for verification during login.
    
    Args:
        plain_text: The plain text password from user registration/reset
    
    Returns:
        Complete Argon2 hash string (e.g., "$argon2id$v=19$m=131072,t=2,p=2$...") for database storage
    """
    return ph.hash(plain_text)


# --- Verification Function ---
def verify_password(stored_hash: str, plain_text: str) -> bool:
    """
    Verify a login attempt by comparing plain text input against the stored hash.
    Argon2 extracts the salt from the stored hash and recomputes the hash to compare.
    
    Args:
        stored_hash: The Argon2 hash string from database
        plain_text: The password entered by user at login
    
    Returns:
        True if password matches, False if wrong or invalid hash
    
    Handles three error cases:
    - VerifyMismatchError: Valid hash, but password doesn't match (normal wrong password)
    - VerificationError: Hash is valid Argon2 but something else failed
    - InvalidHashError: String isn't even a valid Argon2 hash (database corruption)
    """
    try:
        ph.verify(stored_hash, plain_text)
        return True
    except VerifyMismatchError:
        # Wrong password - this is a normal, expected case
        return False
    except VerificationError:
        # Hash is valid Argon2 format but verification failed for other reasons
        return False
    except InvalidHashError:
        # The stored string isn't a valid Argon2 hash (corrupted data in DB)
        return False


# --- Rehashing Function ---
def check_needs_rehash(stored_hash: str) -> bool:
    """
    Check if a stored hash was created with outdated/weaker Argon2 parameters.
    
    Use this function after successful login:
    1. User logs in successfully
    2. Call this function with their stored hash
    3. If True, rehash their password immediately with current parameters
    
    This allows gradual migration to stronger parameters without forcing password resets.
    
    Args:
        stored_hash: The Argon2 hash from database
    
    Returns:
        True if hash is outdated and should be rehashed, False if current
    """
    return ph.check_needs_rehash(stored_hash)


# --- Benchmark Function ---
def benchmark():
    """
    Performance test to verify Argon2 parameters are appropriate.
    
    Hashing should take at least 200ms per password to be resistant to brute force attacks.
    If hashing is too fast (<200ms):
    - Increase time_cost (iterations)
    - Increase memory_cost (memory usage)
    - Increase parallelism (threads)
    
    Run this periodically to ensure parameters haven't become too weak as hardware improves.
    """
    start = time.time()
    # Hash the same test password 10 times to measure average performance
    for _ in range(10):
        ph.hash("benchmark_password")

    # Calculate average time per hash in milliseconds
    avg = (time.time() - start) / 10
    print(f"{avg * 1000:.1f}ms per hash")