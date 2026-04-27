from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
import os

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
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if name and email and password and confirm_password:
            if '@' in email and '.' in email:
                if password == confirm_password:
                    print("Registration successful!")
                else:
                    flash("Passwords do not match.")
                    return render_template('register.html', username=name, email=email)
            else:
                flash("Invalid email address.")
                return render_template('register.html', username=name, email=email)
        else:
            flash("All fields are required.")
            return render_template('register.html', username=name, email=email)

    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True, port=5001)