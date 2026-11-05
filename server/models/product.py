import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Float,
    Integer,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    sku = Column(String(50), nullable=True, unique=True)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    prices = relationship(
        "ProductPrice", back_populates="product", cascade="all, delete-orphan"
    )


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    currency_code = Column(
        String(3),
        ForeignKey("currencies.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    price = Column(Numeric(12, 4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product = relationship("Product", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("product_id", "currency_code", name="uq_product_currency"),
    )
