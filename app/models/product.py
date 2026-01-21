from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Numeric, event
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
import uuid

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    stock = Column(Integer, default=0, nullable=False)
    photo_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    attributes = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="products")

    def __repr__(self):
        return f"<Product {self.name}>"


# Trigger para generar SKU automáticamente
@event.listens_for(Product, 'before_insert')
def generate_sku(mapper, connection, target):
    """
    Genera automáticamente un SKU único si no está proporcionado.
    Formato: ORG{org_id}-{timestamp}-{random}
    Ejemplo: ORG1-202401201530-A7F2
    """
    if not target.sku:
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        random_suffix = uuid.uuid4().hex[:4].upper()
        target.sku = f"ORG{target.org_id}-{timestamp}-{random_suffix}"