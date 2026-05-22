import re
from secrets import choice, randbelow, SystemRandom

PASSWORD_LENGTH = 16


def check_password(pw):
    msg = ''
    # Reject non-ASCII entirely at the top of your function
    if not pw.isascii():
        msg += "Password must contain ASCII characters only. "
    if " " in pw:
        msg += "Password cannot contain spaces. "
    if len(pw) < PASSWORD_LENGTH:
        msg += f"Password must be at least {PASSWORD_LENGTH} characters long. "
    if len(pw) > 128:
        msg += "Password must be no longer than 128 characters. "
    if not re.search(r"[A-Z]", pw):
        msg += "Password must contain at least one uppercase letter. "
    if not re.search(r"[a-z]", pw):
        msg += "Password must contain at least one lowercase letter. "
    if not re.search(r"[0-9]", pw):
        msg += "Password must contain at least one number. "
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?/`~\"'\\]", pw):
        msg += "Must contain at least one special character. "
    if msg:
        return False, msg.strip()
    return True, "Strong password!"