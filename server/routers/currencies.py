from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.schemas.currency import (
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyResponse,
    ExchangeRateCreate,
    ExchangeRateResponse,
)
from server.services.currency_service import CurrencyService

router = APIRouter(tags=["Currencies"])


@router.get("/currencies", response_model=List[CurrencyResponse])
def list_currencies(is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    """
    List all supported currencies in the catalog.
    Optionally filter by active status.
    """
    return CurrencyService.get_currencies(db, is_active=is_active)


@router.post(
    "/currencies", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED
)
def create_currency(currency_in: CurrencyCreate, db: Session = Depends(get_db)):
    """
    Define a new supported currency in the catalog using ISO 4217 validation.
    """
    return CurrencyService.create_currency(db, currency_in)


@router.get("/currencies/{currency_id_or_code}", response_model=CurrencyResponse)
def get_currency(currency_id_or_code: str, db: Session = Depends(get_db)):
    """
    Get currency configuration by ID or 3-letter currency code.
    """
    curr = CurrencyService.get_currency_by_id_or_code(db, currency_id_or_code)
    if not curr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
        )
    return curr


@router.put("/currencies/{currency_id_or_code}", response_model=CurrencyResponse)
def update_currency(
    currency_id_or_code: str, currency_in: CurrencyUpdate, db: Session = Depends(get_db)
):
    """
    Update currency properties (symbol, active status, base currency designation).
    """
    return CurrencyService.update_currency(db, currency_id_or_code, currency_in)


@router.delete(
    "/currencies/{currency_id_or_code}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_currency(currency_id_or_code: str, db: Session = Depends(get_db)):
    """
    Delete a currency configuration from the catalog. Base currency cannot be deleted.
    """
    CurrencyService.delete_currency(db, currency_id_or_code)
    return None


# Exchange Rates Endpoints
@router.get("/exchange-rates", response_model=List[ExchangeRateResponse])
def list_exchange_rates(
    is_active: Optional[bool] = None, db: Session = Depends(get_db)
):
    """
    List all configured exchange rates.
    """
    return CurrencyService.get_exchange_rates(db, is_active=is_active)


@router.post(
    "/exchange-rates",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_exchange_rate(
    rate_in: ExchangeRateCreate, db: Session = Depends(get_db)
):
    """
    Create or update an exchange rate entry between two ISO 4217 currencies.
    """
    return CurrencyService.create_or_update_exchange_rate(db, rate_in)
