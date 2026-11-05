import uuid
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.models.currency import Currency, ExchangeRate
from server.schemas.currency import CurrencyCreate, CurrencyUpdate, ExchangeRateCreate


class CurrencyService:
    @staticmethod
    def get_currencies(db: Session, is_active: Optional[bool] = None) -> List[Currency]:
        query = db.query(Currency)
        if is_active is not None:
            query = query.filter(Currency.is_active == is_active)
        return query.order_by(Currency.is_base.desc(), Currency.code.asc()).all()

    @staticmethod
    def get_currency_by_id_or_code(db: Session, identifier: str) -> Optional[Currency]:
        curr = db.query(Currency).filter(Currency.id == identifier).first()
        if not curr:
            curr = (
                db.query(Currency).filter(Currency.code == identifier.upper()).first()
            )
        return curr

    @staticmethod
    def get_base_currency(db: Session) -> Optional[Currency]:
        base = (
            db.query(Currency)
            .filter(Currency.is_base == True, Currency.is_active == True)
            .first()
        )
        if not base:
            base = db.query(Currency).filter(Currency.code == "USD").first()
        return base

    @staticmethod
    def create_currency(db: Session, currency_in: CurrencyCreate) -> Currency:
        existing = db.query(Currency).filter(Currency.code == currency_in.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency with code '{currency_in.code}' already exists",
            )

        if currency_in.is_base:
            # Set other currencies is_base = False
            db.query(Currency).filter(Currency.is_base == True).update(
                {"is_base": False}
            )

        new_currency = Currency(
            id=str(uuid.uuid4()),
            code=currency_in.code,
            symbol=currency_in.symbol,
            is_base=currency_in.is_base,
            is_active=currency_in.is_active,
        )
        db.add(new_currency)
        db.commit()
        db.refresh(new_currency)
        return new_currency

    @staticmethod
    def update_currency(
        db: Session, identifier: str, currency_in: CurrencyUpdate
    ) -> Currency:
        curr = CurrencyService.get_currency_by_id_or_code(db, identifier)
        if not curr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
            )

        # Edge case: Deactivating a currency currently assigned as Primary Base Currency is blocked
        if currency_in.is_active is False and curr.is_base:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot deactivate the Primary Base Currency. Designate a new base currency first.",
            )

        if currency_in.is_base is True:
            # Demote existing base currency
            db.query(Currency).filter(
                Currency.id != curr.id, Currency.is_base == True
            ).update({"is_base": False})
            curr.is_base = True
            curr.is_active = True  # Base currency must be active
        elif currency_in.is_base is False and curr.is_base:
            # Cannot un-base without assigning another
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot remove base status without designating another currency as base",
            )

        if currency_in.symbol is not None:
            curr.symbol = currency_in.symbol
        if currency_in.is_active is not None and not (
            curr.is_base and not currency_in.is_active
        ):
            curr.is_active = currency_in.is_active

        db.commit()
        db.refresh(curr)
        return curr

    @staticmethod
    def delete_currency(db: Session, identifier: str) -> None:
        curr = CurrencyService.get_currency_by_id_or_code(db, identifier)
        if not curr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
            )

        if curr.is_base:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot delete the Primary Base Currency.",
            )

        db.delete(curr)
        db.commit()

    @staticmethod
    def get_exchange_rates(
        db: Session, is_active: Optional[bool] = None
    ) -> List[ExchangeRate]:
        query = db.query(ExchangeRate)
        if is_active is not None:
            query = query.filter(ExchangeRate.is_active == is_active)
        return query.all()

    @staticmethod
    def get_exchange_rate(
        db: Session, from_code: str, to_code: str
    ) -> Optional[Decimal]:
        from_code = from_code.upper()
        to_code = to_code.upper()
        if from_code == to_code:
            return Decimal("1.000000")

        rate_obj = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency_code == from_code,
                ExchangeRate.to_currency_code == to_code,
                ExchangeRate.is_active == True,
            )
            .first()
        )

        if rate_obj:
            return Decimal(str(rate_obj.rate))

        # Check inverse
        inv_rate_obj = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency_code == to_code,
                ExchangeRate.to_currency_code == from_code,
                ExchangeRate.is_active == True,
            )
            .first()
        )

        if inv_rate_obj and inv_rate_obj.rate > 0:
            return Decimal("1.000000") / Decimal(str(inv_rate_obj.rate))

        return None

    @staticmethod
    def create_or_update_exchange_rate(
        db: Session, rate_in: ExchangeRateCreate
    ) -> ExchangeRate:
        from_code = rate_in.from_currency_code.upper()
        to_code = rate_in.to_currency_code.upper()

        existing = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency_code == from_code,
                ExchangeRate.to_currency_code == to_code,
            )
            .first()
        )

        if existing:
            existing.rate = rate_in.rate
            existing.is_active = rate_in.is_active
            db.commit()
            db.refresh(existing)
            return existing

        new_rate = ExchangeRate(
            id=str(uuid.uuid4()),
            from_currency_code=from_code,
            to_currency_code=to_code,
            rate=rate_in.rate,
            is_active=rate_in.is_active,
        )
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate
