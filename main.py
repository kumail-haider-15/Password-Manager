from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
import os
from database import user_exists, add_user, return_password, load_user, User
from password_handling import check_password, hash_password, verify_password

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.user_loader(load_user)


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
                        login_user(user)
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
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True, port=5001)