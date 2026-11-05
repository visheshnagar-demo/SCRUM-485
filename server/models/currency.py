import uuid
from sqlalchemy import Column, String, Boolean, Numeric, DateTime, func
from server.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(3), unique=True, nullable=False, index=True)
    symbol = Column(String(8), nullable=False)
    is_base = Column(Boolean, default=False, nullable=False)
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


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency_code = Column(String(3), nullable=False, index=True)
    to_currency_code = Column(String(3), nullable=False, index=True)
    rate = Column(Numeric(12, 6), nullable=False)
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
