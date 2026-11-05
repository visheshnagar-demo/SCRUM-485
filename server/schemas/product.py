import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator


class ProductPriceBase(BaseModel):
    currency_code: str
    price: float
    is_active: bool = True

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Invalid ISO 4217 currency code")
        code = v.strip().upper()
        if not re.match(r"^[A-Z]{3}$", code):
            raise ValueError("Invalid ISO 4217 currency code")
        return code

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v is None or v < 0:
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        return round(float(v), 4)


class ProductPriceCreate(ProductPriceBase):
    pass


class ProductPriceUpdate(BaseModel):
    price: Optional[float] = None
    is_active: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError(
                "Price must be a positive decimal value greater than or equal to 0.00"
            )
        if v is not None:
            return round(float(v), 4)
        return v


class ProductPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    currency_code: str
    price: float
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LocalizedPriceInfo(BaseModel):
    currency_code: str
    symbol: str
    price: float
    formatted_price: str
    is_converted: bool = False
    is_fallback: bool = False
    exchange_rate_used: Optional[float] = None
    base_currency_code: str
    base_price: float


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    rating: float = 0.0
    reviews_count: int = 0
    in_stock: bool = True


class ProductCreate(ProductBase):
    id: Optional[str] = None
    base_price: Optional[float] = None  # If provided, creates initial base price


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    in_stock: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    rating: float
    reviews_count: int
    in_stock: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    prices: List[ProductPriceResponse] = []


class ProductWithLocalizedPrice(ProductResponse):
    localized_price: Optional[LocalizedPriceInfo] = None


class ProductListResponse(BaseModel):
    items: List[ProductWithLocalizedPrice]
    total: int
    selected_currency: str
