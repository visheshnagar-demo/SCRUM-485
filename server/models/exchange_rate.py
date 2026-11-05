import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from server.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency = Column(
        String(3),
        ForeignKey("currencies.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_currency = Column(
        String(3),
        ForeignKey("currencies.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rate = Column(Numeric(12, 6), nullable=False)
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

    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", name="uq_exchange_rate_pair"),
    )
