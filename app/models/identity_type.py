# app/models/identity_type.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class IdentityType(Base):
    __tablename__ = "identity_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)  # RUC, DNI, PASSPORT
    name = Column(String(100), nullable=False)              # Nombre legible
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="identity_type")
