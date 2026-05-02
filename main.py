from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
import os
from database import user_exists, add_user
from password_handling import check_password, hash_password, verify_password

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO Verify email later
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        strong, message = check_password(pw=password)

        if name and email and password and confirm_password:
            if '@' in email and '.' in email:
                if strong:
                    if password == confirm_password:
                        if not user_exists(email):
                            hashed_password = hash_password(plain_text=password)
                            add_user(name=name, email=email, password=hashed_password)
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
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True, port=5001)