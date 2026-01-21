## app/models/organization.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

# Many-to-many relationship: Organization Roles for employees
org_employee_roles = Table(
    'org_employee_roles',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('organization_employees.id', ondelete='CASCADE'), primary_key=True),
    Column('org_role_id', Integer, ForeignKey('organization_roles.id', ondelete='CASCADE'), primary_key=True)
)

class OrganizationRole(Base):
    __tablename__ = "organization_roles"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="roles")
    employees = relationship("OrganizationEmployee", secondary=org_employee_roles, back_populates="roles")

    def __repr__(self):
        return f"<OrganizationRole {self.name}>"

class OrganizationEmployee(Base):
    __tablename__ = "organization_employees"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="employees")
    user = relationship("User", back_populates="org_employees")
    roles = relationship("OrganizationRole", secondary=org_employee_roles, back_populates="employees")

    def __repr__(self):
        return f"<OrganizationEmployee user_id={self.user_id} org_id={self.org_id}>"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    legal_name = Column(String(255), nullable=False)
    org_type = Column(String(100), nullable=False)
    description = Column(Text)
    code_telephone = Column(String(10))
    telephone = Column(String(20))
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    primary_color = Column(String(7), default='#000000')
    secondary_color = Column(String(7), default='#FFFFFF')
    tertiary_color = Column(String(7), default='#F0F0F0')
    employee_count = Column(Integer, default=0)
    address = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    extra_data = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_organizations")
    employees = relationship("OrganizationEmployee", back_populates="organization", cascade="all, delete-orphan")
    roles = relationship("OrganizationRole", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"