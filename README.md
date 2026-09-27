# 🔐 Password Manager

A secure, full-stack password management web application built with **Python and Flask**. The project was developed to practice backend development, database management, authentication, authorization, cryptography, session management, and secure web-application design.

Users can create an account, verify their email, securely store website credentials, manage multiple accounts for the same website, generate strong passwords, retrieve stored credentials, and reset their account password.

> **Project Status:** Completed

---

## 📌 Overview

The Flask Password Manager provides a centralized place for users to securely manage their website credentials.

The application separates two different types of password protection:

* **Account/login passwords** are stored using secure password hashing.
* **Stored website passwords** are encrypted so they can be decrypted when the user needs to retrieve them.

The application also implements authentication, user-specific authorization, time-limited verification/reset tokens, password-strength validation, and session timeout handling.

---

## ✨ Features

### User Authentication

* User registration
* Password-strength validation
* Password confirmation
* Secure password hashing
* User login and logout
* Protected routes using Flask-Login
* Email verification
* Time-limited email-verification tokens
* Forgot-password workflow
* Time-limited password-reset tokens

### Password Management

* Add website credentials
* View saved websites
* Store multiple accounts for the same website
* Prevent duplicate website + username/email combinations
* View credentials for a selected website
* Show/hide stored passwords
* Copy usernames and passwords to the clipboard
* Generate strong random passwords
* Delete stored credentials

### Security

* Authentication with Flask-Login
* Route protection with `@login_required`
* User-specific authorization using `current_user.id`
* Password hashing for account credentials
* Encryption for stored website passwords
* Time-limited verification and reset tokens
* Session inactivity timeout
* Secret configuration through environment variables
* HTTP-only / SameSite / Secure cookie configuration can be enabled according to the deployment environment

---

## 🛠️ Technologies Used

### Backend

* **Python**
* **Flask**
* **Flask-SQLAlchemy**
* **SQLAlchemy**
* **Flask-Login**
* **Flask-Mail**
* **itsdangerous**
* **python-dotenv**

### Database

* **SQLite**

### Frontend

* **HTML5**
* **CSS3**
* **JavaScript**

### Security / Cryptography

* Password hashing
* Symmetric encryption for stored credentials
* Signed and time-limited tokens
* Flask session management

---

## 🔐 Security Design

### Account Passwords

User login passwords are **hashed**, rather than stored as plaintext.

A hash is one-way and is appropriate for passwords that only need to be verified during login.

```text
User Password
      ↓
   Hashing
      ↓
Database
```

During login:

```text
Entered Password
      ↓
Verification
      ↓
Stored Password Hash
      ↓
Match?
```

---

### Stored Website Passwords

Website credentials must be retrieved later, so hashing alone cannot be used for these passwords.

Instead:

```text
Plain Website Password
          ↓
       Encryption
          ↓
       Database
```

When the user needs to retrieve the credential:

```text
Encrypted Password
          ↓
       Decryption
          ↓
      User Request
```

The database therefore does not store the website password as plaintext.

---

### Authorization

Authentication answers:

> "Who is the user?"

Authorization answers:

> "Is this user allowed to access this particular record?"

Password queries are scoped to the currently authenticated user.

Conceptually:

```python
Password.user_id == current_user.id
```

This prevents a logged-in user from accessing another user's password records simply by changing an ID or URL parameter.

---

### Email Verification and Password Reset

The application uses signed, time-limited tokens for account verification and password-reset workflows.

Tokens are generated using `itsdangerous` and are validated with an expiration time.

Example design:

```text
Generate Token
      ↓
Send Email
      ↓
User Opens Link
      ↓
Validate Signature
      ↓
Check Expiration
      ↓
Perform Requested Action
```

---

### Session Management

The application implements a server-side inactivity timeout.

The server records the most recent activity timestamp and checks it before processing requests.

```text
Incoming Request
       ↓
before_request
       ↓
Check last activity
       ↓
15-minute inactivity?
    /          \
  Yes           No
   ↓             ↓
 Logout       Continue
```

The logout process clears the Flask-Login authentication state and session data.

---

## 📂 Project Structure

```text
Password-Manager/
│
├── main.py
├── database.py
├── password_hashing.py
├── password_encryption.py
├── password_handling.py
├── verify_email.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── password_view.html
│   ├── forget_password.html
│   ├── reset_password.html
│   
│
└── static/
    ├── CSS/
    │   └── style.css
    │
    └── JS/
        └── script.js
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Password-Manager
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your_secret_key
FERNET_KEY=your_fernet_key
MY_EMAIL=your_email@example.com
PASSWORD=your_email_app_password
```

## ▶️ Running the Application

Start the Flask application:

```bash
python main.py
```

The development server will run on the configured local port.

Open the application in your browser:

```text
http://127.0.0.1:<PORT>
```

Replace `<PORT>` with the port configured in your application.

---

## 🧪 Testing

The application was tested through both normal user workflows and security-focused scenarios.

### Functional Testing

* Registration
* Email verification
* Login
* Logout
* Password creation
* Password generation
* Multiple accounts for the same website
* Show/hide password
* Copy credentials
* Password deletion
* Forgot-password flow
* Password reset
* Session timeout

### Security Testing

* Accessing protected routes without authentication
* Attempting to access another user's password record
* Testing password ownership through `user_id`
* Invalid and expired verification tokens
* Invalid and expired password-reset tokens
* Invalid login credentials
* Invalid form submissions
* Session expiration after inactivity
* Checking that stored vault passwords are not saved as plaintext in the database

---

## 🔍 Important Security Considerations

This project is primarily a **learning and portfolio project** demonstrating secure application concepts.

It should **not be presented as a production-ready password manager** without additional security engineering and independent security review.

Potential areas for further hardening include:

* CSRF protection for state-changing requests
* Login and password-reset rate limiting
* HTTPS-only deployment
* Secure production cookie configuration
* Stronger key-management architecture
* Database backups and recovery
* Security logging and monitoring
* Automated security and integration testing
* Additional protection around password-reveal operations
* Formal threat modeling and security review

These are natural next steps for taking the application beyond its current portfolio scope.

---

## 🧠 What I Learned

This project helped me move from writing individual Python programs toward thinking about complete web applications.

Major learning areas included:

* Building web applications with Flask
* Designing database models and relationships
* SQLAlchemy queries
* Authentication and authorization
* Password hashing versus encryption
* Session management
* Signed and time-limited tokens
* Email-based verification and password recovery
* Frontend and backend interaction
* JavaScript DOM manipulation
* Debugging multi-record interfaces
* Preventing unauthorized database access
* Handling application errors and invalid input
* Thinking about security from an attacker's perspective
* Structuring a project for GitHub and portfolio presentation

---

## 🚧 Known Limitations

The application is intentionally scoped as a portfolio project.

Current limitations include:

* SQLite is suitable for this project's scope but is not intended as the final database architecture for a larger production system.
* The application has not undergone a professional penetration test or independent security audit.
* Some production-grade controls, such as comprehensive CSRF protection and rate limiting, would still be required before handling real users at scale.

---

## 🔮 Future Improvements

Possible future improvements include:

* REST API architecture
* Automated unit and integration tests
* CSRF protection
* Login and reset-request rate limiting
* PostgreSQL deployment
* Production HTTPS configuration
* Docker containerization
* CI/CD pipeline
* Security event logging
* Better secret/key management
* Password re-authentication before sensitive operations
* Improved password-reveal security
* Search and filtering for large password collections
* Deployment to a cloud platform

---

## 🌐 Live Demo

**Live Demo:** `<ADD_DEPLOYED_APPLICATION_URL>`

---

## ⭐ Project Purpose

This project was created as a practical demonstration of Python backend development, Flask, database integration, authentication, authorization, cryptography, and secure web-application development.