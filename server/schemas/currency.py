from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

# Comprehensive ISO 4217 currency codes
ISO_4217_CODES = {
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLP",
    "CNY",
    "COP",
    "CRC",
    "CUC",
    "CUP",
    "CVE",
    "CZK",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "GBP",
    "GEL",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KMF",
    "KPW",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRU",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLL",
    "SOS",
    "SRD",
    "SSP",
    "STN",
    "SVC",
    "SYP",
    "SZL",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "UYU",
    "UZS",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XCD",
    "XOF",
    "XPF",
    "YER",
    "ZAR",
    "ZMW",
    "ZWL",
}


class CurrencyBase(BaseModel):
    code: str
    symbol: str
    is_base: bool = False
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_iso_code(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Invalid ISO 4217 currency code")
        code_upper = v.strip().upper()
        if len(code_upper) != 3 or code_upper not in ISO_4217_CODES:
            raise ValueError("Invalid ISO 4217 currency code")
        return code_upper


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    symbol: Optional[str] = None
    is_base: Optional[bool] = None
    is_active: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExchangeRateBase(BaseModel):
    from_currency_code: str
    to_currency_code: str
    rate: Decimal
    is_active: bool = True

    @field_validator("from_currency_code", "to_currency_code")
    @classmethod
    def validate_rate_codes(cls, v: str) -> str:
        code_upper = v.strip().upper()
        if code_upper not in ISO_4217_CODES:
            raise ValueError("Invalid ISO 4217 currency code")
        return code_upper

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Exchange rate must be greater than 0")
        return v


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateUpdate(BaseModel):
    rate: Optional[Decimal] = None
    is_active: Optional[bool] = None

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Exchange rate must be greater than 0")
        return v


class ExchangeRateResponse(ExchangeRateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
