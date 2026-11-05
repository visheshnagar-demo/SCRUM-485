import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from server.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    base_price = Column(Numeric(12, 4), nullable=False)
    base_currency_code = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(500), nullable=True)
    rating = Column(Numeric(3, 2), default=5.0, nullable=False)
    reviews_count = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
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
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("product_id", "currency_code", name="uq_product_currency"),
    )

    product = relationship("Product", back_populates="prices")
