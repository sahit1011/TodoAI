from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from backend.database import Base
from backend.config import ASSISTANT_MODES

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preferred_assistant_mode = Column(String(10), default=ASSISTANT_MODES["ACT"])

    # Relationship
    tasks = relationship("Task", back_populates="user")
