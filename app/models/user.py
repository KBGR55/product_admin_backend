## app/models/user.py
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class IdentityType(enum.Enum):
    RUC = "RUC"
    PASSPORT = "PASSPORT"
    FOREIGN_ID = "FOREIGN_ID"

class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class RoleType(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    MODERATOR = "MODERATOR"
    EDITOR = "EDITOR"

# Many-to-many relationship table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Relationship with User
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    identity_number = Column(String(50), unique=True, nullable=False, index=True)
    identity_type = Column(Enum(IdentityType), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    created_at = Column(Date, default=datetime.now)
    
    # Relationships
    account = relationship("Account", back_populates="user", uselist=False)
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    organizations = relationship("Organization", secondary="user_organizations", back_populates="members", foreign_keys="user_organizations.c.user_id")
    owned_organizations = relationship("Organization", foreign_keys="Organization.owner_id", back_populates="owner")
    org_employees = relationship("OrganizationEmployee", back_populates="user")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"