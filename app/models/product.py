## app/models/product.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    cost = Column(Float)
    stock = Column(Integer, default=0)
    photo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    attributes = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="products")

    def __repr__(self):
        return f"<Product {self.name}>"