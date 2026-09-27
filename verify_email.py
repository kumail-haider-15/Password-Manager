# Email Verification and Password Reset Module
# Handles sending secure email links for account verification and password recovery.
# Uses URLSafeTimedSerializer to generate tokens that expire after 30 minutes.

from flask import url_for
from flask_mail import Message


def send_verification_email(email, s, mail):
    """
    Send an email verification link to a new user during registration.
    
    The verification process:
    1. User registers with email and password
    2. This function generates a secure token containing the email
    3. Token is embedded in a verification URL
    4. User clicks the link in their email
    5. Token is validated and email is marked as verified
    
    Args:
        email: User's email address
        s: URLSafeTimedSerializer instance for creating secure tokens
        mail: Flask-Mail instance for sending emails
    
    Token Details:
    - Token is signed with 'email-verify' salt for verification links
    - Token expires in 1800 seconds (30 minutes) as per max_age in verify_email route
    - Each token is unique and can only be used once successfully
    """
    # Create a secure token containing the email address
    token = s.dumps(email, salt='email-verify')

    # Generate the full verification URL (e.g., https://example.com/verify/token123)
    # _external=True ensures the full URL is generated (required for email links)
    link = url_for('verify_email', token=token, _external=True)

    # Create and send the email message
    msg = Message('Verify your email', recipients=[email])
    msg.body = f'Click to verify: {link}'
    mail.send(msg)


def send_reset_password_email(email, s, mail):
    """
    Send a password reset link to a user who has forgotten their password.
    
    The password reset process:
    1. User requests password reset with their email
    2. This function generates a secure token containing the email
    3. Token is embedded in a reset URL
    4. User clicks the link in their email
    5. User enters new password (which is validated for strength)
    6. Password is hashed and stored, token is invalidated
    
    Args:
        email: User's email address
        s: URLSafeTimedSerializer instance for creating secure tokens
        mail: Flask-Mail instance for sending emails
    
    Token Details:
    - Token is signed with 'password-reset' salt for reset links
    - Token expires in 1800 seconds (30 minutes) as per max_age in reset_password route
    - Using a different salt than email verification prevents token reuse
    - If user doesn't reset within 30 minutes, they must request a new link
    """
    # Create a secure token containing the email address
    token = s.dumps(email, salt='password-reset')

    # Generate the full password reset URL (e.g., https://example.com/reset_password/token123)
    # _external=True ensures the full URL is generated (required for email links)
    link = url_for('reset_password', token=token, _external=True)

    # Create and send the email message
    msg = Message('Reset your password', recipients=[email])
    msg.body = f'Click to reset password: {link}'
    mail.send(msg)