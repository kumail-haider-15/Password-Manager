from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import time

# --- Configuration ---
# Create one instance, reuse it everywhere
ph = PasswordHasher(
    time_cost=2,  # number of passes over memory
    memory_cost=131072,  # memory usage in KB → this is 64MB
    parallelism=2,  # number of threads used
    hash_len=32,  # length of the final hash in bytes
    salt_len=16  # length of random salt in bytes
)


# --- Hashing ---
def hash_password(plain_text: str) -> str:
    """
    Takes a plain text password, returns a full argon2 hash string.
    Store this string directly in your database.
    """
    return ph.hash(plain_text)


# --- Verification ---
def verify_password(stored_hash: str, plain_text: str) -> bool:
    """
    Compares a plain text input against the stored hash.
    Returns True if matched, False if wrong password.
    """
    try:
        ph.verify(stored_hash, plain_text)
        return True
    except VerifyMismatchError:
        # Wrong password — normal case
        return False
    except VerificationError:
        # Hash is valid argon2 but something else went wrong
        return False
    except InvalidHashError:
        # The stored string isn't even a valid argon2 hash
        return False


# --- Rehashing (important — explained below) ---
def check_needs_rehash(stored_hash: str) -> bool:
    """
    Returns True if the hash was created with old/weaker parameters.
    Call this after a successful login and rehash if True.
    """
    return ph.check_needs_rehash(stored_hash)


def benchmark():
    """To check parameters are outdated or not by determining the time taken to hash a password. If it's too fast (under 200ms), you may want to increase time_cost or memory_cost."""
    start = time.time()
    for _ in range(10):
        ph.hash("benchmark_password")

    avg = (time.time() - start) / 10
    print(f"{avg * 1000:.1f}ms per hash")