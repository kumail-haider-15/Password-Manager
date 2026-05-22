from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


# ─── Base ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# ─── Users Table ────────────────────────────────────────
class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship
    passwords: Mapped[list["Password"]] = relationship(back_populates="user")


# ─── Saved Passwords Table ─────────────────────────────────────────
class Password(Base):
    __tablename__ = "saved_passwords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    website: Mapped[str] = mapped_column(String(255), nullable=False)
    email_or_username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    # Foreign key
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="passwords")


def add_user(user: object):
    db.session.add(user)
    db.session.commit()


def user_exists(email: str):
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if user:
        return True, user
    return False, None


def return_password(email: str):
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if user:
        return user.password
    return None