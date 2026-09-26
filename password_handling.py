# Password Strength Validation Module
# Enforces strict security requirements for user passwords.
# This module checks passwords BEFORE hashing to ensure they meet security standards.

import re
from secrets import choice, randbelow, SystemRandom

# Minimum password length requirement
PASSWORD_LENGTH = 16


def check_password_strength(pw):
    """
    Validate that a password meets all security requirements.
    
    Requirements:
    - ASCII characters only (no unicode)
    - No spaces
    - Minimum 16 characters, maximum 128 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one number (0-9)
    - At least one special character (!@#$%^&*...etc)
    
    Args:
        pw: The password to validate
    
    Returns:
        Tuple of (is_strong: bool, message: str)
        - If strong: (True, "Strong password!")
        - If weak: (False, "Error message(s) explaining requirements")
    """
    msg = ''

    # Reject non-ASCII characters entirely
    if not pw.isascii():
        msg += "Password must contain ASCII characters only. "

    # Prevent spaces to avoid whitespace issues
    if " " in pw:
        msg += "Password cannot contain spaces. "

    # Enforce minimum length
    if len(pw) < PASSWORD_LENGTH:
        msg += f"Password must be at least {PASSWORD_LENGTH} characters long. "

    # Prevent excessively long passwords
    if len(pw) > 128:
        msg += "Password must be no longer than 128 characters. "

    # Require at least one uppercase letter
    if not re.search(r"[A-Z]", pw):
        msg += "Password must contain at least one uppercase letter. "

    # Require at least one lowercase letter
    if not re.search(r"[a-z]", pw):
        msg += "Password must contain at least one lowercase letter. "

    # Require at least one digit
    if not re.search(r"[0-9]", pw):
        msg += "Password must contain at least one number. "

    # Require at least one special character
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?/`~\"'\\]", pw):
        msg += "Must contain at least one special character. "

    # Return validation result
    if msg:
        return False, msg.strip()
    return True, "Strong password!"