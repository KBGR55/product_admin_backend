# app/models/user.py
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)

    identity_number = Column(String(50), unique=True, nullable=False)
    identity_type_id = Column(Integer, ForeignKey("identity_types.id"), nullable=False)

    gender_id = Column(Integer, ForeignKey("genders.id"), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    identity_type = relationship("IdentityType", back_populates="users")
    gender = relationship("Gender")

    account = relationship("Account", back_populates="user", uselist=False)
    org_employees = relationship("OrganizationEmployee", back_populates="user")
    owned_organizations = relationship("Organization", back_populates="owner")
