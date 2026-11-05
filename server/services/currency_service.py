import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from server.models.currency import Currency
from server.schemas.currency import CurrencyCreate, CurrencyUpdate


class CurrencyService:
    @staticmethod
    def get_by_id_or_code(db: Session, identifier: str) -> Optional[Currency]:
        ident = identifier.strip()
        return (
            db.query(Currency)
            .filter(
                or_(
                    Currency.id == ident,
                    Currency.code == ident.upper(),
                )
            )
            .first()
        )

    @staticmethod
    def get_base_currency(db: Session) -> Optional[Currency]:
        base = (
            db.query(Currency)
            .filter(Currency.is_base == True, Currency.is_active == True)
            .first()
        )
        if not base:
            base = db.query(Currency).filter(Currency.is_base == True).first()
        if not base:
            base = db.query(Currency).filter(Currency.code == "USD").first()
        if not base:
            base = db.query(Currency).first()
        return base

    @staticmethod
    def list_currencies(
        db: Session, active_only: bool = False, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Currency], int]:
        query = db.query(Currency)
        if active_only:
            query = query.filter(Currency.is_active == True)
        total = query.count()
        items = (
            query.order_by(Currency.is_base.desc(), Currency.code.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    @staticmethod
    def create_currency(db: Session, currency_in: CurrencyCreate) -> Currency:
        code = currency_in.code.strip().upper()
        existing = db.query(Currency).filter(Currency.code == code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Currency code '{code}' already exists.",
            )

        # If this is designated as base currency, reset existing base currencies
        if currency_in.is_base:
            db.query(Currency).filter(Currency.is_base == True).update(
                {"is_base": False}
            )
            db.commit()

        # If this is the very first currency added, make it base by default
        is_first = db.query(Currency).count() == 0
        is_base = currency_in.is_base or is_first

        currency = Currency(
            id=str(uuid.uuid4()),
            code=code,
            name=currency_in.name or code,
            symbol=currency_in.symbol,
            is_base=is_base,
            is_active=currency_in.is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(currency)
        db.commit()
        db.refresh(currency)
        return currency

    @staticmethod
    def update_currency(
        db: Session, identifier: str, currency_in: CurrencyUpdate
    ) -> Currency:
        currency = CurrencyService.get_by_id_or_code(db, identifier)
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency '{identifier}' not found.",
            )

        # Edge case: Deactivating a currency currently assigned as Primary Base Currency is blocked
        if (
            currency_in.is_active is False
            and currency.is_base
            and currency_in.is_base is not True
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot deactivate primary base currency. Select a new base currency first.",
            )

        if currency_in.is_base is True:
            # Demote any other base currency
            db.query(Currency).filter(
                Currency.id != currency.id, Currency.is_base == True
            ).update({"is_base": False})
            currency.is_base = True
            currency.is_active = True  # Base currency must be active
        elif currency_in.is_base is False and currency.is_base:
            # Cannot un-base without selecting another base
            other_active = (
                db.query(Currency)
                .filter(Currency.id != currency.id, Currency.is_active == True)
                .first()
            )
            if not other_active:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot unset base currency when no other active currency exists to be base.",
                )
            currency.is_base = False

        if currency_in.name is not None:
            currency.name = currency_in.name
        if currency_in.symbol is not None:
            currency.symbol = currency_in.symbol
        if currency_in.is_active is not None and not (
            currency.is_base and currency_in.is_active is False
        ):
            currency.is_active = currency_in.is_active

        currency.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(currency)
        return currency

    @staticmethod
    def delete_currency(db: Session, identifier: str) -> None:
        currency = CurrencyService.get_by_id_or_code(db, identifier)
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency '{identifier}' not found.",
            )

        if currency.is_base:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the primary base currency.",
            )

        db.delete(currency)
        db.commit()
