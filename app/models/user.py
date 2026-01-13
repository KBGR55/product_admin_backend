## app/models/user.py
from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class IdentityType(enum.Enum):
    RUC = "RUC"
    DNI = "DNI"
    PASSPORT = "PASSPORT"
    FOREIGN_ID = "FOREIGN_ID"

class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    identity_number = Column(String(50), unique=True, nullable=False)
    identity_type = Column(Enum(IdentityType), nullable=False)
    gender = Column(Enum(Gender), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    
    account = relationship("Account", back_populates="user", uselist=False)
    org_employees = relationship("OrganizationEmployee", back_populates="user")
    owned_organizations = relationship("Organization", back_populates="owner")
