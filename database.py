from sqlalchemy import create_engine, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# ─── Base ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Engine ─────────────────────────────────────────────
engine = create_engine("sqlite:///myapp.db", echo=False)


# ─── Users Table ────────────────────────────────────────
class User(Base):
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

with Session(engine) as session:
    pass