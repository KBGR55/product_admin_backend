# app/models/gender.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Gender(Base):
    __tablename__ = "genders"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)  # MALE, FEMALE
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="gender")
