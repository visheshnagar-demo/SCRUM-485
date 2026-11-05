from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from server.schemas.currency import ISO_4217_CODES


class ProductPriceBase(BaseModel):
    currency_code: str
    price: Decimal
    is_active: bool = True

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        code_upper = v.strip().upper()
        if code_upper not in ISO_4217_CODES:
            raise ValueError("Invalid ISO 4217 currency code")
        return code_upper

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0.00"):
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        return v


class ProductPriceCreate(ProductPriceBase):
    pass


class ProductPriceUpdate(BaseModel):
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < Decimal("0.00"):
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        return v


class ProductPriceResponse(ProductPriceBase):
    id: str
    product_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Decimal
    base_currency_code: str = "USD"
    is_active: bool = True
    image_url: Optional[str] = None
    rating: Decimal = Decimal("5.0")
    reviews_count: int = 0

    @field_validator("base_price")
    @classmethod
    def validate_base_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0.00"):
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        return v

    @field_validator("base_currency_code")
    @classmethod
    def validate_base_currency(cls, v: str) -> str:
        code_upper = v.strip().upper()
        if code_upper not in ISO_4217_CODES:
            raise ValueError("Invalid ISO 4217 currency code")
        return code_upper


class ProductCreate(ProductBase):
    id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = None
    base_currency_code: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    rating: Optional[Decimal] = None
    reviews_count: Optional[int] = None

    @field_validator("base_price")
    @classmethod
    def validate_base_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < Decimal("0.00"):
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        return v

    @field_validator("base_currency_code")
    @classmethod
    def validate_base_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            code_upper = v.strip().upper()
            if code_upper not in ISO_4217_CODES:
                raise ValueError("Invalid ISO 4217 currency code")
            return code_upper
        return v


class LocalizedPriceDetail(BaseModel):
    currency_code: str
    symbol: str
    price: Decimal
    formatted_price: str
    is_explicit: bool
    is_converted: bool
    is_fallback: bool
    exchange_rate: Optional[Decimal] = None
    original_currency_code: str
    original_price: Decimal


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    prices: List[ProductPriceResponse] = []
    localized_price: Optional[LocalizedPriceDetail] = None

    model_config = ConfigDict(from_attributes=True)
