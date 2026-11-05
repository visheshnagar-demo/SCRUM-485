import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.models.product import Product, ProductPrice
from server.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductPriceCreate,
    ProductPriceUpdate,
    LocalizedPriceDetail,
)
from server.services.currency_service import CurrencyService


class PricingService:
    @staticmethod
    def format_price(amount: Decimal, symbol: str, code: str) -> str:
        # Round to 2 decimal places for standard display
        rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if code in ("JPY", "KRW"):
            return f"{symbol}{int(amount):,}"
        return f"{symbol}{rounded:,.2f}"

    @staticmethod
    def calculate_localized_price(
        db: Session, product: Product, target_currency_code: Optional[str] = None
    ) -> LocalizedPriceDetail:
        base_curr = CurrencyService.get_base_currency(db)
        base_code = product.base_currency_code or (
            base_curr.code if base_curr else "USD"
        )
        base_symbol = base_curr.symbol if base_curr else "$"

        if not target_currency_code:
            target_currency_code = base_code

        target_code = target_currency_code.upper()
        target_curr = CurrencyService.get_currency_by_id_or_code(db, target_code)

        # 1. Check if product has an explicit active price for this currency
        explicit_price = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product.id,
                ProductPrice.currency_code == target_code,
                ProductPrice.is_active == True,
            )
            .first()
        )

        if explicit_price:
            sym = target_curr.symbol if target_curr else "$"
            price_val = Decimal(str(explicit_price.price))
            return LocalizedPriceDetail(
                currency_code=target_code,
                symbol=sym,
                price=price_val,
                formatted_price=PricingService.format_price(
                    price_val, sym, target_code
                ),
                is_explicit=True,
                is_converted=False,
                is_fallback=False,
                exchange_rate=None,
                original_currency_code=base_code,
                original_price=Decimal(str(product.base_price)),
            )

        # 2. Check if target is base currency
        if target_code == base_code:
            price_val = Decimal(str(product.base_price))
            return LocalizedPriceDetail(
                currency_code=base_code,
                symbol=base_symbol,
                price=price_val,
                formatted_price=PricingService.format_price(
                    price_val, base_symbol, base_code
                ),
                is_explicit=True,
                is_converted=False,
                is_fallback=False,
                exchange_rate=Decimal("1.000000"),
                original_currency_code=base_code,
                original_price=price_val,
            )

        # 3. Dynamic conversion via Exchange Rate
        rate = CurrencyService.get_exchange_rate(db, base_code, target_code)
        if rate is not None:
            converted_price = (Decimal(str(product.base_price)) * rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            sym = target_curr.symbol if target_curr else "$"
            return LocalizedPriceDetail(
                currency_code=target_code,
                symbol=sym,
                price=converted_price,
                formatted_price=PricingService.format_price(
                    converted_price, sym, target_code
                ),
                is_explicit=False,
                is_converted=True,
                is_fallback=False,
                exchange_rate=rate,
                original_currency_code=base_code,
                original_price=Decimal(str(product.base_price)),
            )

        # 4. Fallback to Primary Base Currency
        price_val = Decimal(str(product.base_price))
        return LocalizedPriceDetail(
            currency_code=base_code,
            symbol=base_symbol,
            price=price_val,
            formatted_price=PricingService.format_price(
                price_val, base_symbol, base_code
            ),
            is_explicit=False,
            is_converted=False,
            is_fallback=True,
            exchange_rate=None,
            original_currency_code=base_code,
            original_price=price_val,
        )

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        currency_code: Optional[str] = None,
    ) -> List[dict]:
        query = db.query(Product).filter(Product.is_active == True)
        if category:
            query = query.filter(Product.category == category)
        products = query.offset(skip).limit(limit).all()

        results = []
        for p in products:
            p_dict = {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "base_price": p.base_price,
                "base_currency_code": p.base_currency_code,
                "is_active": p.is_active,
                "image_url": p.image_url,
                "rating": p.rating,
                "reviews_count": p.reviews_count,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "prices": [
                    {
                        "id": pr.id,
                        "product_id": pr.product_id,
                        "currency_code": pr.currency_code,
                        "price": pr.price,
                        "is_active": pr.is_active,
                        "created_at": pr.created_at,
                        "updated_at": pr.updated_at,
                    }
                    for pr in p.prices
                ],
                "localized_price": PricingService.calculate_localized_price(
                    db, p, currency_code
                ),
            }
            results.append(p_dict)
        return results

    @staticmethod
    def get_product_by_id(
        db: Session, product_id: str, currency_code: Optional[str] = None
    ) -> Optional[dict]:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return None
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "base_price": p.base_price,
            "base_currency_code": p.base_currency_code,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "rating": p.rating,
            "reviews_count": p.reviews_count,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "prices": [
                {
                    "id": pr.id,
                    "product_id": pr.product_id,
                    "currency_code": pr.currency_code,
                    "price": pr.price,
                    "is_active": pr.is_active,
                    "created_at": pr.created_at,
                    "updated_at": pr.updated_at,
                }
                for pr in p.prices
            ],
            "localized_price": PricingService.calculate_localized_price(
                db, p, currency_code
            ),
        }

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        pid = product_in.id or str(uuid.uuid4())
        existing = db.query(Product).filter(Product.id == pid).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID '{pid}' already exists",
            )

        new_prod = Product(
            id=pid,
            name=product_in.name,
            description=product_in.description,
            category=product_in.category,
            base_price=product_in.base_price,
            base_currency_code=product_in.base_currency_code,
            is_active=product_in.is_active,
            image_url=product_in.image_url,
            rating=product_in.rating,
            reviews_count=product_in.reviews_count,
        )
        db.add(new_prod)
        db.commit()
        db.refresh(new_prod)
        return new_prod

    @staticmethod
    def update_product(
        db: Session, product_id: str, product_in: ProductUpdate
    ) -> Product:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if product_in.name is not None:
            p.name = product_in.name
        if product_in.description is not None:
            p.description = product_in.description
        if product_in.category is not None:
            p.category = product_in.category
        if product_in.base_price is not None:
            p.base_price = product_in.base_price
        if product_in.base_currency_code is not None:
            p.base_currency_code = product_in.base_currency_code
        if product_in.is_active is not None:
            p.is_active = product_in.is_active
        if product_in.image_url is not None:
            p.image_url = product_in.image_url
        if product_in.rating is not None:
            p.rating = product_in.rating
        if product_in.reviews_count is not None:
            p.reviews_count = product_in.reviews_count

        db.commit()
        db.refresh(p)
        return p

    @staticmethod
    def delete_product(db: Session, product_id: str) -> None:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        db.delete(p)
        db.commit()

    @staticmethod
    def get_product_prices(db: Session, product_id: str) -> List[ProductPrice]:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return (
            db.query(ProductPrice).filter(ProductPrice.product_id == product_id).all()
        )

    @staticmethod
    def set_product_price(
        db: Session, product_id: str, price_in: ProductPriceCreate
    ) -> ProductPrice:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        currency_code = price_in.currency_code.upper()
        # Verify currency exists in supported currencies
        curr = CurrencyService.get_currency_by_id_or_code(db, currency_code)
        if not curr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency '{currency_code}' is not configured in catalog",
            )

        existing = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product_id,
                ProductPrice.currency_code == currency_code,
            )
            .first()
        )

        if existing:
            existing.price = price_in.price
            existing.is_active = price_in.is_active
            db.commit()
            db.refresh(existing)
            return existing

        new_price = ProductPrice(
            id=str(uuid.uuid4()),
            product_id=product_id,
            currency_code=currency_code,
            price=price_in.price,
            is_active=price_in.is_active,
        )
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        return new_price

    @staticmethod
    def update_product_price(
        db: Session,
        product_id: str,
        price_id_or_code: str,
        price_in: ProductPriceUpdate,
    ) -> ProductPrice:
        p_price = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product_id,
                ProductPrice.id == price_id_or_code,
            )
            .first()
        )

        if not p_price:
            p_price = (
                db.query(ProductPrice)
                .filter(
                    ProductPrice.product_id == product_id,
                    ProductPrice.currency_code == price_id_or_code.upper(),
                )
                .first()
            )

        if not p_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product price record not found",
            )

        if price_in.price is not None:
            p_price.price = price_in.price
        if price_in.is_active is not None:
            p_price.is_active = price_in.is_active

        db.commit()
        db.refresh(p_price)
        return p_price

    @staticmethod
    def delete_product_price(
        db: Session, product_id: str, price_id_or_code: str
    ) -> None:
        p_price = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product_id,
                ProductPrice.id == price_id_or_code,
            )
            .first()
        )

        if not p_price:
            p_price = (
                db.query(ProductPrice)
                .filter(
                    ProductPrice.product_id == product_id,
                    ProductPrice.currency_code == price_id_or_code.upper(),
                )
                .first()
            )

        if not p_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product price record not found",
            )

        db.delete(p_price)
        db.commit()
