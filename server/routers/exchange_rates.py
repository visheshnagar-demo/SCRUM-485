import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.exchange_rate import ExchangeRate
from server.schemas.exchange_rate import (
    ExchangeRateCreate,
    ExchangeRateUpdate,
    ExchangeRateResponse,
    ExchangeRateListResponse,
)

router = APIRouter(prefix="/api/v1/exchange-rates", tags=["Exchange Rates"])


@router.get("", response_model=ExchangeRateListResponse)
def list_exchange_rates(
    active_only: bool = Query(False),
    from_currency: Optional[str] = Query(None),
    to_currency: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(ExchangeRate)
    if active_only:
        query = query.filter(ExchangeRate.is_active == True)
    if from_currency:
        query = query.filter(ExchangeRate.from_currency == from_currency.upper())
    if to_currency:
        query = query.filter(ExchangeRate.to_currency == to_currency.upper())

    total = query.count()
    items = (
        query.order_by(ExchangeRate.from_currency.asc()).offset(skip).limit(limit).all()
    )
    return ExchangeRateListResponse(
        items=[ExchangeRateResponse.model_validate(r) for r in items],
        total=total,
    )


@router.post(
    "", response_model=ExchangeRateResponse, status_code=status.HTTP_201_CREATED
)
def create_exchange_rate(rate_in: ExchangeRateCreate, db: Session = Depends(get_db)):
    from_curr = rate_in.from_currency.upper()
    to_curr = rate_in.to_currency.upper()

    # Ensure currencies exist or allow standard ISO
    existing = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.from_currency == from_curr,
            ExchangeRate.to_currency == to_curr,
        )
        .first()
    )

    if existing:
        # Update existing
        existing.rate = rate_in.rate
        existing.is_active = rate_in.is_active
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return ExchangeRateResponse.model_validate(existing)

    rate_rec = ExchangeRate(
        id=str(uuid.uuid4()),
        from_currency=from_curr,
        to_currency=to_curr,
        rate=rate_in.rate,
        is_active=rate_in.is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(rate_rec)
    db.commit()
    db.refresh(rate_rec)
    return ExchangeRateResponse.model_validate(rate_rec)


@router.get("/{rate_id}", response_model=ExchangeRateResponse)
def get_exchange_rate(rate_id: str, db: Session = Depends(get_db)):
    rate_rec = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
    if not rate_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate record '{rate_id}' not found.",
        )
    return ExchangeRateResponse.model_validate(rate_rec)


@router.put("/{rate_id}", response_model=ExchangeRateResponse)
def update_exchange_rate(
    rate_id: str,
    rate_in: ExchangeRateUpdate,
    db: Session = Depends(get_db),
):
    rate_rec = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
    if not rate_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate record '{rate_id}' not found.",
        )

    if rate_in.rate is not None:
        rate_rec.rate = rate_in.rate
    if rate_in.is_active is not None:
        rate_rec.is_active = rate_in.is_active

    rate_rec.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rate_rec)
    return ExchangeRateResponse.model_validate(rate_rec)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange_rate(rate_id: str, db: Session = Depends(get_db)):
    rate_rec = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
    if not rate_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate record '{rate_id}' not found.",
        )
    db.delete(rate_rec)
    db.commit()
    return None
