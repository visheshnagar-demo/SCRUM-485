import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator


class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    is_active: bool = True

    @field_validator("from_currency", "to_currency")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Invalid ISO 4217 currency code")
        code = v.strip().upper()
        if not re.match(r"^[A-Z]{3}$", code):
            raise ValueError("Invalid ISO 4217 currency code")
        return code

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        if v is None or v <= 0:
            raise ValueError("Exchange rate must be a positive number greater than 0")
        return round(float(v), 6)


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateUpdate(BaseModel):
    rate: Optional[float] = None
    is_active: Optional[bool] = None

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Exchange rate must be a positive number greater than 0")
        if v is not None:
            return round(float(v), 6)
        return v


class ExchangeRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_currency: str
    to_currency: str
    rate: float
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExchangeRateListResponse(BaseModel):
    items: List[ExchangeRateResponse]
    total: int
