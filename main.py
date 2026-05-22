from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
import os
from database import user_exists, add_user, return_password, User, db, Password
from password_handling import check_password
from password_hashing import hash_password, verify_password
from password_encryption import encrypt_password, decrypt_password
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=10)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Configure Flask-Login to handle the redirect message elegantly
login_manager.login_view = "login"  # Tells it where your login route is
login_manager.login_message = "Your session has expired due to inactivity. Please log in again."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myapp.db"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.before_request
def refresh_session_lifetime():
    # This flags the current session to update its expiration
    # date right now, shifting the 15-minute window forward.
    session.permanent = True


@app.route('/auth/ping', methods=['POST'])
def session_ping():
    # Returning an empty string with a 204 status code tells the JavaScript fetch API
    # "Success, no content to display." Flask consumes this and stops.
    return '', 204


@app.route('/js-error')
def js_error():
    return "<h1>JavaScript is Required</h1><p>This password manager requires JavaScript to securely manage your vault sessions.</p>"


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
                        session.permanent = True
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

        strong, message = check_password(pw=password)
        exists, user = user_exists(email=email)

        if name and email and password and confirm_password:
            if '@' in email and '.' in email:
                if strong:
                    if password == confirm_password:
                        if not exists:
                            hashed_password = hash_password(plain_text=password)
                            new_user = User(name=name, email=email, password=hashed_password)
                            add_user(user=new_user)
                            session.permanent = True
                            login_user(user=new_user)
                            print("Registration successful!")
                            return redirect(url_for('dashboard'))
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


@app.route('/dashboard')
@login_required
def dashboard():
    user_passwords = db.session.execute(db.select(Password).filter_by(user_id=current_user.id)).scalars().all()
    db.session.expunge_all()
    for p in user_passwords:
        p.password = decrypt_password(p.password)
    return render_template('dashboard.html', passwords=user_passwords)


@app.route('/add_password', methods=['POST'])
@login_required
def add_password():
    website_name = request.form.get('website')
    email_or_username = request.form.get('email_or_username')
    password = request.form.get('password')
    if website_name and email_or_username and password:
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
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True, port=5001)