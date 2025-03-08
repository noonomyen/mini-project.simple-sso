from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship
from flask_login import UserMixin
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base, UserMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    full_name = Column(String(256), nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    password = Column(String(72), nullable=False)
    registered_at = Column(DateTime, default=datetime.now)

    applications = relationship("Application", back_populates="owner", cascade="all, delete-orphan")
    application_redeem_tokens = relationship("ApplicationRedeemToken", back_populates="user", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    owner = relationship("User", back_populates="applications")
    application_redeem_tokens = relationship("ApplicationRedeemToken", back_populates="application", cascade="all, delete-orphan")

class ApplicationRedeemToken(Base):
    __tablename__ = "application_redeem_token"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("application.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), nullable=False)
    used = Column(Boolean, default=False)
    auth_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="application_redeem_tokens")
    application = relationship("Application", back_populates="application_redeem_tokens")
