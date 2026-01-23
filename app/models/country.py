from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    code = Column(String(5), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone_code = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Country {self.code} - {self.name}>"