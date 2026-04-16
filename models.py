from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

session_jig = Table(
    "session_jig", Base.metadata,
    Column("session_id", Integer, ForeignKey("borrow_sessions.id")),
    Column("jig_id", Integer, ForeignKey("jigs.id")),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

class JIG(Base):
    __tablename__ = "jigs"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    image_url = Column(String, default="")
    qr_code_url = Column(String, default="")       # Fixed QR (admin phát hành)
    status = Column(String(20), default="available") # available / in_use
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BorrowSession(Base):
    __tablename__ = "borrow_sessions"
    id = Column(Integer, primary_key=True)
    session_token = Column(String(64), unique=True, nullable=False)
    session_qr_url = Column(String, default="")    # Session QR (trả JIG)
    borrower_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    jigs = relationship("JIG", secondary=session_jig)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    action = Column(String(20), nullable=False)    # borrow / return
    user_name = Column(String(100), nullable=False)
    jig_names = Column(Text, default="")
    session_token = Column(String(64), default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    jig_id = Column(Integer, ForeignKey("jigs.id"), nullable=True)
    author_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    jig = relationship("JIG")