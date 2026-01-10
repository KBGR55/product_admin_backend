from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
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
    
    # Relationship with Account
    account = relationship("Account", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"