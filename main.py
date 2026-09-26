# Password Manager Flask Application
# This application provides user authentication, email verification, password storage,
# and encryption/decryption capabilities for managing passwords securely.

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
import os
from database import user_exists, add_user, return_password, User, db, Password, is_verified
from password_handling import check_password_strength
from password_hashing import hash_password, verify_password
from password_encryption import encrypt_password, decrypt_password
from sqlalchemy import select
from flask_mail import Mail
from verify_email import send_verification_email, send_reset_password_email
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Session timeout configuration - sets automatic logout after 3 minutes of inactivity
SESSION_TIMEOUT_TIMEPERIOD = 5

# Time must be passed before resending verification email (in minutes)
TIME_BEFORE_RESEND_EMAIL = 30

# Security: Prevent JavaScript from reading the session cookie (XSS protection)
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Security: Prevent cross-site requests from freely sending the cookie (CSRF protection)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# HTTPS: Set to True when the deployed website uses HTTPS (currently False for local development)
app.config['SESSION_COOKIE_SECURE'] = True

# Email configuration for sending verification and password reset emails via Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MY_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MY_EMAIL')

# Initialize Flask-Mail for sending emails
mail = Mail(app)

# Initialize serializer for creating secure tokens (email verification, password reset)
s = URLSafeTimedSerializer(app.secret_key)


# Configure Flask-Login for user session management
login_manager = LoginManager()
login_manager.init_app(app)


# User loader callback - retrieves the current user from database using their ID
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# SQLite database configuration and initialization
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myapp.db"
db.init_app(app)

# Create all database tables if they don't exist
with app.app_context():
    db.create_all()


# Session timeout check - runs before each request to logout inactive users
@app.before_request
def check_session_timeout():
    if current_user.is_authenticated:

        last_activity = session.get('last_activity')

        if last_activity:

            last_activity = datetime.fromisoformat(last_activity)

            inactive_time = datetime.now() - last_activity

            # Logout user if inactive for the specified timeout period
            if inactive_time > timedelta(minutes=SESSION_TIMEOUT_TIMEPERIOD):
                logout_user()
                session.clear()

                login_url = url_for('login')

                return f'Your session has expired due to inactivity, login to continue <a href="{login_url}">Login</a>'

        # Update last activity timestamp for the current request
        session['last_activity'] = datetime.now().isoformat()
    return None


@app.route('/')
def home():
    # Display the home/landing page
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle user login - validate email format and password, authenticate against database
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        exists, user = user_exists(email=email)
        if email and password:
            if '@' in email and '.' in email:
                if exists:
                    saved_hashed_password = return_password(email=email)
                    # Verify the provided password against the stored hash
                    if verify_password(stored_hash=saved_hashed_password, plain_text=password):
                        login_user(user=user)
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Invalid Password.")
                        return render_template('login.html', email=email)
                else:
                    flash("Email does not exists.")
                    return render_template('login.html', email=email)
            else:
                flash("Invalid email address.")
                return render_template('login.html', email=email)
        else:
            flash("Both fields are required.")
            return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    # Logout the current user and clear all session data
    logout_user()
    session.clear()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle user registration - validate inputs, check password strength, prevent duplicates, send verification email
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check password strength against security requirements
        strong, message = check_password_strength(pw=password)
        exists, user = user_exists(email=email)

        if name and email and password and confirm_password:
            if '@' in email and '.' in email:
                if strong:
                    if password == confirm_password:
                        if not exists:
                            # Create new user and send verification email
                            add_user(email=email, name=name, password=hash_password(password), date_time=datetime.now())

                            send_verification_email(email=email, s=s, mail=mail)
                            return "We have send you an email, check your inbox and verify your email"

                        elif not is_verified(email=email):
                            # If user exists but unverified, allow re-registration and resend email if 30+ minutes passed
                            add_user(email=email, name=name, password=hash_password(password), date_time=datetime.now())
                            user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

                            difference = datetime.now() - user.date_time
                            # Extract minutes from the time difference (format: HH:MM:SS)
                            difference = str(difference).split(':')[1]

                            # Only resend email if TIME_BEFORE_RESEND_EMAIL have passed since last registration attempt
                            if int(difference) >= TIME_BEFORE_RESEND_EMAIL:
                                send_verification_email(email=email, s=s, mail=mail)
                                user.date_time = datetime.now()
                                db.session.commit()
                            return "We have send you an email, check your inbox and verify your email"

                        else:
                            flash("This email already exists. Login instead.")
                            return render_template('register.html', username=name, email=email)

                    else:
                        flash("Passwords do not match.")
                        return render_template('register.html', username=name, email=email)
                else:
                    flash(message)
                    return render_template('register.html', username=name, email=email)
            else:
                flash("Invalid email address.")
                return render_template('register.html', username=name, email=email)
        else:
            flash("All fields are required.")
            return render_template('register.html', username=name, email=email)

    return render_template('register.html')


@app.route('/verify/<token>')
def verify_email(token):
    # Verify user's email using the token sent in verification email (expires in 30 minutes)
    try:
        email = s.loads(token, salt='email-verify', max_age=1800)

    except SignatureExpired:
        return "This reset link has expired."

    except BadSignature:
        return "This reset link is invalid."

    # Mark user as verified and log them in
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    user.is_verified = True
    db.session.commit()
    login_user(user=user)
    print("Registration successful!")

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Display user's passwords grouped by website
    user_passwords = db.session.execute(db.select(Password).filter_by(user_id=current_user.id)).scalars().all()
    password_groups = {}

    # Make the dictionary where the key is the name of website and the value is the number of accounts per website

    for password in user_passwords:
        if password.website not in password_groups:
            password_groups[password.website] = 0

        password_groups[password.website] += 1

    return render_template('dashboard.html', passwords=password_groups)


@app.route('/password_view/<website_name>', methods=['GET'])
@login_required
def password_view(website_name):
    # Fetch and display all passwords info for a specific website
    passwords = db.session.execute(
        select(Password.id,
               Password.website,
               Password.email_or_username,
               Password.user_id).where(
            Password.user_id == current_user.id,
            Password.website == website_name
        )
    ).scalars().all()

    if passwords:

        return render_template('password_view.html', passwords=passwords, website_name=website_name)
    else:
        return "Unauthorized or password not found."


@app.route('/add_password', methods=['POST'])
@login_required
def add_password():
    # Add a new password entry - validate inputs and prevent duplicate website/username combinations
    website_name = request.form.get('website').capitalize()
    email_or_username = request.form.get('email_or_username')
    password = request.form.get('password')
    user_passwords = db.session.execute(db.select(Password).filter_by(user_id=current_user.id)).scalars().all()
    duplication = False
    if website_name and email_or_username and password:

        # Check if this website/username combination already exists for the user
        for user_password in user_passwords:
            if user_password.website == website_name and user_password.email_or_username == email_or_username:
                duplication = True
        if duplication:
            flash("This website and email/username combination already exists.")
        else:
            # Encrypt the password before storing in database
            encrypted_pass = encrypt_password(plain_text=password)
            new_password = Password(website=website_name, email_or_username=email_or_username, password=encrypted_pass,
                                    user_id=current_user.id)
            db.session.add(new_password)
            db.session.commit()
    else:
        flash("All fields are required")
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:password_id>')
@login_required
def delete_password(password_id):
    # Delete a specific password entry and redirect to appropriate page
    password = db.session.get(Password, password_id)
    if password and password.user_id == current_user.id:
        db.session.delete(password)
        db.session.commit()
    else:
        flash("Unauthorized or password not found")

    # Check if there are other passwords for the same website
    passwords = db.session.execute(
        select(Password).where(
            Password.user_id == current_user.id,
            Password.website == password.website
        )
    ).scalars().all()

    # Redirect to website's password list if entries remain, otherwise return to dashboard
    if passwords:
        return redirect(url_for('password_view', website_name=password.website))
    else:
        return redirect(url_for('dashboard'))


@app.route("/get-password/<int:password_id>")
@login_required
def get_password(password_id):
    # API endpoint to retrieve and decrypt a specific password (used by frontend via AJAX)
    password = db.session.get(Password, password_id)

    if not password:
        return {"error": "Password not found"}, 404

    # Verify user authorization
    if password.user_id != current_user.id:
        return {"error": "Unauthorized"}, 403

    # Decrypt and return the password
    decrypted_password = decrypt_password(encrypted_text=password.password)

    return {"password": decrypted_password}


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    # Handle password reset request - send reset link via email if user exists
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Please enter email")
        elif '@' not in email and '.' not in email:
            flash("Enter valid email address")
        elif email:
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
            if user:
                # Send password reset email with secure token (expires in 30 minutes)
                send_reset_password_email(email=email, s=s, mail=mail)
                return "A password reset link has been sent to your email."
            else:
                flash("This email does not exists")

    return render_template('forget_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Handle password reset using secure token from email link (token expires in 30 minutes)
    try:
        email = s.loads(token, salt='password-reset', max_age=1800)
    except SignatureExpired:
        return "This reset link has expired."

    except BadSignature:
        return "This reset link is invalid."

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate new password meets strength requirements
        strong, message = check_password_strength(pw=password)
        if password and confirm_password:
            if strong:
                if password == confirm_password:
                    # Update user's password with new hash
                    user.password = hash_password(plain_text=password)
                    db.session.commit()
                    login_url = url_for('login')

                    return f'Password reset successfully, login now <a href="{login_url}">Login</a>'

                else:
                    flash('Passwords do not match')
            else:
                flash(message)
        else:
            flash("Please fill all the fields")

    return render_template('reset_password.html')


if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True, port=5001)