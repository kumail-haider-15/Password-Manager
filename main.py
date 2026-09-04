from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
import os

from tenacity import retry_if_exception

from database import user_exists, add_user, return_password, User, db, Password, is_verified
from password_handling import check_password_strength
from password_hashing import hash_password, verify_password
from password_encryption import encrypt_password, decrypt_password
from sqlalchemy import select
from flask_mail import Mail
from verify_email import send_verification_email, send_reset_password_email
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MY_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MY_EMAIL')

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myapp.db"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        exists, user = user_exists(email=email)
        if email and password:
            if '@' in email and '.' in email:
                if exists:
                    saved_hashed_password = return_password(email=email)
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
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO Verify email later
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        strong, message = check_password_strength(pw=password)
        exists, user = user_exists(email=email)

        if name and email and password and confirm_password:
            if '@' in email and '.' in email:
                if strong:
                    if password == confirm_password:
                        if not exists:
                            add_user(email=email, name=name, password=hash_password(password), date_time=datetime.now())

                            send_verification_email(email=email, s=s, mail=mail)
                            return "We have send you an email, check your inbox and verify your email"

                        elif not is_verified(email=email):
                            add_user(email=email, name=name, password=hash_password(password), date_time=datetime.now())
                            user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

                            difference = datetime.now() - user.date_time
                            # for hour, it is 0, for minute it is 1 and for seconds it is 2
                            difference = str(difference).split(':')[1]

                            if int(difference) >= 30:
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
    try:
        email = s.loads(token, salt='email-verify', max_age=1800)

    except SignatureExpired:
        return "This reset link has expired."

    except BadSignature:
        return "This reset link is invalid."

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    user.is_verified = True
    db.session.commit()
    login_user(user=user)
    print("Registration successful!")

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_passwords = db.session.execute(db.select(Password).filter_by(user_id=current_user.id)).scalars().all()
    password_groups = {}

    for password in user_passwords:

        if password.website not in password_groups:
            password_groups[password.website] = []

        password_groups[password.website].append(password)

    return render_template('dashboard.html', passwords=password_groups)


@app.route('/password_view/<website_name>', methods=['GET'])
@login_required
def password_view(website_name):
    passwords = db.session.execute(
        select(Password).where(
            Password.user_id == current_user.id,
            Password.website == website_name
        )
    ).scalars().all()

    if passwords:
        db.session.expunge_all()
        for password in passwords:
            password.password = decrypt_password(password.password)
        return render_template('password_view.html', passwords=passwords, website_name=website_name)
    else:
        return "Unauthorized or password not found."


@app.route('/add_password', methods=['POST'])
@login_required
def add_password():
    website_name = request.form.get('website').capitalize()
    email_or_username = request.form.get('email_or_username')
    password = request.form.get('password')
    user_passwords = db.session.execute(db.select(Password).filter_by(user_id=current_user.id)).scalars().all()
    duplication = False
    if website_name and email_or_username and password:

        for user_password in user_passwords:
            if user_password.website == website_name and user_password.email_or_username == email_or_username:
                duplication = True
        if duplication:
            flash("This website and email/username combination already exists.")
        else:
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
    password = db.session.get(Password, password_id)
    if password and password.user_id == current_user.id:
        db.session.delete(password)
        db.session.commit()
    else:
        flash("Unauthorized or password not found")
    passwords = db.session.execute(
        select(Password).where(
            Password.user_id == current_user.id,
            Password.website == password.website
        )
    ).scalars().all()
    if passwords:
        return redirect(url_for('password_view', website_name=password.website))
    else:
        return redirect(url_for('dashboard'))


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Please enter email")
        elif '@' not in email and '.' not in email:
            flash("Enter valid email address")
        elif email:
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
            if user:
                send_reset_password_email(email=email, s=s, mail=mail)
                return "A password reset link has been sent to your email."
            else:
                flash("This email does not exists")

    return render_template('forget_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
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

        strong, message = check_password_strength(pw=password)
        if password and confirm_password:
            if strong:
                if password == confirm_password:
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
    app.run(debug=True, port=5001)