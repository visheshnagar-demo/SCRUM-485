from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.schemas.currency import (
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyResponse,
    CurrencyListResponse,
)
from server.services.currency_service import CurrencyService

router = APIRouter(prefix="/api/v1/currencies", tags=["Currencies"])


@router.get("", response_model=CurrencyListResponse)
def get_currencies(
    active_only: bool = Query(False, description="Filter for active currencies only"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items, total = CurrencyService.list_currencies(
        db, active_only=active_only, skip=skip, limit=limit
    )
    return CurrencyListResponse(
        items=[CurrencyResponse.model_validate(c) for c in items],
        total=total,
    )


@router.get("/base", response_model=CurrencyResponse)
def get_base_currency(db: Session = Depends(get_db)):
    base = CurrencyService.get_base_currency(db)
    if not base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No base currency configured in the system.",
        )
    return CurrencyResponse.model_validate(base)


@router.post("", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_currency(currency_in: CurrencyCreate, db: Session = Depends(get_db)):
    currency = CurrencyService.create_currency(db, currency_in)
    return CurrencyResponse.model_validate(currency)


@router.get("/{identifier}", response_model=CurrencyResponse)
def get_currency(identifier: str, db: Session = Depends(get_db)):
    currency = CurrencyService.get_by_id_or_code(db, identifier)
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency '{identifier}' not found.",
        )
    return CurrencyResponse.model_validate(currency)


@router.put("/{identifier}", response_model=CurrencyResponse)
def update_currency(
    identifier: str,
    currency_in: CurrencyUpdate,
    db: Session = Depends(get_db),
):
    currency = CurrencyService.update_currency(db, identifier, currency_in)
    return CurrencyResponse.model_validate(currency)


@router.delete("/{identifier}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency(identifier: str, db: Session = Depends(get_db)):
    CurrencyService.delete_currency(db, identifier)
    return None
