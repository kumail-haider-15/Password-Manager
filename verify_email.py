from flask import url_for
from flask_mail import Message


def send_verification_email(email, s, mail):
    token = s.dumps(email, salt='email-verify')
    link = url_for('verify_email', token=token, _external=True)
    msg = Message('Verify your email', recipients=[email])
    msg.body = f'Click to verify: {link}'
    mail.send(msg)