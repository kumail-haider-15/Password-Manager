from sqlalchemy import create_engine, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from flask_login import UserMixin


# ─── Base ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Engine ─────────────────────────────────────────────
engine = create_engine("sqlite:///myapp.db", echo=False)


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
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    # Foreign key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="passwords")


# ─── Create Tables ───────────────────────────────────────
Base.metadata.create_all(engine)


def add_user(user: object):
    with Session(engine) as session:
        session.add(user)
        session.commit()


def user_exists(email: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return True, user
        return False, user


def return_password(email: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(email=email).first()
        return user.password


def load_user(user_id: int):
    with Session(engine) as session:
        return session.query(User).filter_by(id=user_id).first()