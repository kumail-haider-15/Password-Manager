# Database Models and Operations
# Defines SQLAlchemy ORM models for users and their saved passwords.
# Uses SQLAlchemy 2.0+ with modern type hints (Mapped).

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime
from datetime import datetime


# ─── Base Class ─────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    This class is used by SQLAlchemy to construct the ORM mapping.
    """
    pass


# Initialize SQLAlchemy with the custom base class
db = SQLAlchemy(model_class=Base)


# ─── User Model ─────────────────────────────────────────────
class User(UserMixin, Base):
    """
    User account model - represents a registered user in the system.
    
    Inherits from UserMixin which provides Flask-Login integration:
    - is_authenticated: Returns True if user is authenticated
    - is_active: Returns True if user account is active
    - is_anonymous: Returns False (user is not anonymous)
    - get_id(): Returns the user's ID as a string
    
    Attributes:
        id: Unique user identifier (primary key)
        name: User's display name
        email: User's email address (must be unique)
        password: Argon2 hashed password (never store plain text!)
        is_verified: Whether user has verified their email address
        date_time: Timestamp of user creation/last registration attempt
        passwords: Relationship to saved passwords (one-to-many)
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # One-to-many relationship: one user can have many saved passwords
    passwords: Mapped[list["Password"]] = relationship(back_populates="user")


# ─── Password Model ─────────────────────────────────────────
class Password(Base):
    """
    Saved password model - represents a stored password for a website/service.
    
    Each password entry stores:
    - Which website/service it's for
    - The associated username/email for that service
    - The encrypted password (uses Fernet symmetric encryption)
    - Which user owns this password entry
    
    Attributes:
        id: Unique password entry identifier (primary key)
        website: Name of the website/service (e.g., "Gmail", "GitHub")
        email_or_username: Username or email used to log into the website
        password: Encrypted password (encrypted with Fernet, decrypted when viewing)
        user_id: Foreign key reference to the user who owns this password
        user: Relationship back to the User model
    """
    __tablename__ = "saved_passwords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    website: Mapped[str] = mapped_column(String(255), nullable=False)
    email_or_username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Foreign key: links this password to its owner (user.id)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship back to User model
    user: Mapped["User"] = relationship(back_populates="passwords")


# ─── User Operations ────────────────────────────────────────

def add_user(email: str, name: str, password: str, date_time):
    """
    Create a new user or update an existing unverified user's credentials.
    
    This function handles two scenarios:
    1. NEW USER: Email doesn't exist → Creates new User record
    2. EXISTING UNVERIFIED USER: Email exists but not verified → Updates their info
    
    This allows users to register multiple times before email verification.
    Useful for resetting password during registration if they made a mistake.
    
    Args:
        email: User's email address
        name: User's name
        password: Argon2 hashed password (MUST be hashed before calling this function!)
        date_time: Timestamp of registration/update attempt
    
    Returns:
        None (creates/updates database record)
    """
    # Check if user with this email already exists
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if user:
        # Existing user - update their credentials (for re-registration before verification)
        user.name = name
        user.password = password
        db.session.commit()
    else:
        # New user - create account with default is_verified=False
        user = User(name=name, email=email, password=password, is_verified=False, date_time=date_time)
        db.session.add(user)
        db.session.commit()


def user_exists(email: str):
    """
    Check if a user exists in the database.
    
    Args:
        email: Email address to search for
    
    Returns:
        Tuple of (exists: bool, user: User or None)
        - (True, user_object) if user found
        - (False, None) if user not found
    """
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if user:
        return True, user
    return False, None


def is_verified(email: str):
    """
    Check if a user has verified their email address.
    
    Assumes user exists. Use user_exists() first to verify user is in database.
    
    Args:
        email: Email address to check
    
    Returns:
        Boolean indicating verification status
    """
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    return user.is_verified


def return_password(email: str):
    """
    Retrieve the hashed password for a user.
    
    Used during login to get the stored Argon2 hash for password verification.
    The returned hash is compared against the user's login attempt using verify_password().
    
    Args:
        email: Email address of the user
    
    Returns:
        Argon2 hash string if user found, None if user doesn't exist
    """
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if user:
        return user.password
    return None