import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from server.models.product import Product, ProductPrice
from server.models.currency import Currency
from server.models.exchange_rate import ExchangeRate
from server.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductPriceCreate,
    ProductPriceUpdate,
    LocalizedPriceInfo,
    ProductWithLocalizedPrice,
    ProductPriceResponse,
)
from server.services.currency_service import CurrencyService


class PricingService:
    @staticmethod
    def format_currency_amount(amount: float, symbol: str, code: str) -> str:
        # Currency-specific formatting
        if code.upper() == "JPY":
            formatted_num = f"{int(round(amount)):,}"
        else:
            formatted_num = f"{amount:,.2f}"

        if code.upper() == "EUR":
            return f"{symbol}{formatted_num}"
        elif code.upper() == "GBP":
            return f"{symbol}{formatted_num}"
        elif code.upper() == "JPY":
            return f"{symbol}{formatted_num}"
        elif code.upper() == "CAD":
            return f"C${formatted_num}"
        elif code.upper() == "USD":
            return f"${formatted_num}"
        else:
            return f"{symbol}{formatted_num} {code}"

    @staticmethod
    def calculate_localized_price(
        db: Session, product: Product, target_currency_code: Optional[str] = None
    ) -> LocalizedPriceInfo:
        base_curr = CurrencyService.get_base_currency(db)
        base_code = base_curr.code if base_curr else "USD"
        base_symbol = base_curr.symbol if base_curr else "$"

        # Find base price for product
        base_price_rec = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product.id,
                ProductPrice.currency_code == base_code,
                ProductPrice.is_active == True,
            )
            .first()
        )
        base_price = float(base_price_rec.price) if base_price_rec else 0.0

        # If no target currency requested or target is base currency
        req_code = (
            target_currency_code.strip().upper() if target_currency_code else base_code
        )
        target_curr = db.query(Currency).filter(Currency.code == req_code).first()

        target_symbol = target_curr.symbol if target_curr else req_code

        # If requested currency is base currency
        if req_code == base_code:
            return LocalizedPriceInfo(
                currency_code=base_code,
                symbol=base_symbol,
                price=base_price,
                formatted_price=PricingService.format_currency_amount(
                    base_price, base_symbol, base_code
                ),
                is_converted=False,
                is_fallback=False,
                exchange_rate_used=None,
                base_currency_code=base_code,
                base_price=base_price,
            )

        # Check for explicit active price in requested currency
        explicit_price_rec = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product.id,
                ProductPrice.currency_code == req_code,
                ProductPrice.is_active == True,
            )
            .first()
        )

        if explicit_price_rec:
            actual_price = float(explicit_price_rec.price)
            return LocalizedPriceInfo(
                currency_code=req_code,
                symbol=target_symbol,
                price=actual_price,
                formatted_price=PricingService.format_currency_amount(
                    actual_price, target_symbol, req_code
                ),
                is_converted=False,
                is_fallback=False,
                exchange_rate_used=None,
                base_currency_code=base_code,
                base_price=base_price,
            )

        # Fallback to exchange rate conversion
        exchange_rate_rec = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency == base_code,
                ExchangeRate.to_currency == req_code,
                ExchangeRate.is_active == True,
            )
            .first()
        )

        rate = None
        if exchange_rate_rec:
            rate = float(exchange_rate_rec.rate)
        else:
            # Check inverse rate
            inverse_rate_rec = (
                db.query(ExchangeRate)
                .filter(
                    ExchangeRate.from_currency == req_code,
                    ExchangeRate.to_currency == base_code,
                    ExchangeRate.is_active == True,
                )
                .first()
            )
            if inverse_rate_rec and float(inverse_rate_rec.rate) > 0:
                rate = 1.0 / float(inverse_rate_rec.rate)

        if rate is not None:
            converted_price = round(base_price * rate, 4)
            return LocalizedPriceInfo(
                currency_code=req_code,
                symbol=target_symbol,
                price=converted_price,
                formatted_price=PricingService.format_currency_amount(
                    converted_price, target_symbol, req_code
                ),
                is_converted=True,
                is_fallback=False,
                exchange_rate_used=round(rate, 6),
                base_currency_code=base_code,
                base_price=base_price,
            )

        # Edge case: No explicit price and no exchange rate entry exists -> fallback to base currency display
        return LocalizedPriceInfo(
            currency_code=base_code,
            symbol=base_symbol,
            price=base_price,
            formatted_price=PricingService.format_currency_amount(
                base_price, base_symbol, base_code
            ),
            is_converted=False,
            is_fallback=True,
            exchange_rate_used=None,
            base_currency_code=base_code,
            base_price=base_price,
        )

    @staticmethod
    def get_product_with_localized_price(
        db: Session, product: Product, currency_code: Optional[str] = None
    ) -> ProductWithLocalizedPrice:
        loc_price = PricingService.calculate_localized_price(db, product, currency_code)
        price_items = [
            ProductPriceResponse(
                id=p.id,
                product_id=p.product_id,
                currency_code=p.currency_code,
                price=float(p.price),
                is_active=p.is_active,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in product.prices
        ]

        return ProductWithLocalizedPrice(
            id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            sku=product.sku,
            rating=product.rating,
            reviews_count=product.reviews_count,
            in_stock=product.in_stock,
            created_at=product.created_at,
            updated_at=product.updated_at,
            prices=price_items,
            localized_price=loc_price,
        )

    @staticmethod
    def list_products(
        db: Session,
        currency_code: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[ProductWithLocalizedPrice], int, str]:
        base_curr = CurrencyService.get_base_currency(db)
        selected_curr = (
            currency_code.upper()
            if currency_code
            else (base_curr.code if base_curr else "USD")
        )

        query = db.query(Product)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        products = query.order_by(Product.name.asc()).offset(skip).limit(limit).all()

        items = [
            PricingService.get_product_with_localized_price(db, p, selected_curr)
            for p in products
        ]
        return items, total, selected_curr

    @staticmethod
    def get_product(
        db: Session, product_id: str, currency_code: Optional[str] = None
    ) -> ProductWithLocalizedPrice:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found.",
            )
        return PricingService.get_product_with_localized_price(
            db, product, currency_code
        )

    @staticmethod
    def create_product(
        db: Session, product_in: ProductCreate
    ) -> ProductWithLocalizedPrice:
        prod_id = product_in.id or f"prod-{uuid.uuid4().hex[:8]}"
        existing = db.query(Product).filter(Product.id == prod_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with ID '{prod_id}' already exists.",
            )

        product = Product(
            id=prod_id,
            name=product_in.name,
            description=product_in.description,
            category=product_in.category,
            sku=product_in.sku,
            rating=product_in.rating,
            reviews_count=product_in.reviews_count,
            in_stock=product_in.in_stock,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # If base_price was provided in create payload, add base currency price entry
        if product_in.base_price is not None:
            base_curr = CurrencyService.get_base_currency(db)
            base_code = base_curr.code if base_curr else "USD"
            pp = ProductPrice(
                id=str(uuid.uuid4()),
                product_id=product.id,
                currency_code=base_code,
                price=product_in.base_price,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(pp)
            db.commit()
            db.refresh(product)

        return PricingService.get_product_with_localized_price(db, product)

    @staticmethod
    def update_product(
        db: Session, product_id: str, product_in: ProductUpdate
    ) -> ProductWithLocalizedPrice:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found.",
            )

        if product_in.name is not None:
            product.name = product_in.name
        if product_in.description is not None:
            product.description = product_in.description
        if product_in.category is not None:
            product.category = product_in.category
        if product_in.sku is not None:
            product.sku = product_in.sku
        if product_in.rating is not None:
            product.rating = product_in.rating
        if product_in.reviews_count is not None:
            product.reviews_count = product_in.reviews_count
        if product_in.in_stock is not None:
            product.in_stock = product_in.in_stock

        product.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(product)
        return PricingService.get_product_with_localized_price(db, product)

    @staticmethod
    def delete_product(db: Session, product_id: str) -> None:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found.",
            )
        db.delete(product)
        db.commit()

    # Product Prices Operations
    @staticmethod
    def get_prices(db: Session, product_id: str) -> List[ProductPriceResponse]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found.",
            )
        prices = (
            db.query(ProductPrice).filter(ProductPrice.product_id == product_id).all()
        )
        return [
            ProductPriceResponse(
                id=p.id,
                product_id=p.product_id,
                currency_code=p.currency_code,
                price=float(p.price),
                is_active=p.is_active,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in prices
        ]

    @staticmethod
    def set_price(
        db: Session, product_id: str, price_in: ProductPriceCreate
    ) -> ProductPriceResponse:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found.",
            )

        curr_code = price_in.currency_code.strip().upper()
        curr = db.query(Currency).filter(Currency.code == curr_code).first()
        if not curr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency '{curr_code}' is not configured in the catalog.",
            )

        existing = (
            db.query(ProductPrice)
            .filter(
                ProductPrice.product_id == product_id,
                ProductPrice.currency_code == curr_code,
            )
            .first()
        )

        if existing:
            # Idempotent update
            existing.price = price_in.price
            existing.is_active = price_in.is_active
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return ProductPriceResponse(
                id=existing.id,
                product_id=existing.product_id,
                currency_code=existing.currency_code,
                price=float(existing.price),
                is_active=existing.is_active,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
            )

        pp = ProductPrice(
            id=str(uuid.uuid4()),
            product_id=product_id,
            currency_code=curr_code,
            price=price_in.price,
            is_active=price_in.is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(pp)
        db.commit()
        db.refresh(pp)
        return ProductPriceResponse(
            id=pp.id,
            product_id=pp.product_id,
            currency_code=pp.currency_code,
            price=float(pp.price),
            is_active=pp.is_active,
            created_at=pp.created_at,
            updated_at=pp.updated_at,
        )

    @staticmethod
    def update_price(
        db: Session, product_id: str, price_id: str, price_in: ProductPriceUpdate
    ) -> ProductPriceResponse:
        pp = (
            db.query(ProductPrice)
            .filter(ProductPrice.id == price_id, ProductPrice.product_id == product_id)
            .first()
        )
        if not pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price record '{price_id}' for product '{product_id}' not found.",
            )

        if price_in.price is not None:
            pp.price = price_in.price
        if price_in.is_active is not None:
            pp.is_active = price_in.is_active

        pp.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(pp)
        return ProductPriceResponse(
            id=pp.id,
            product_id=pp.product_id,
            currency_code=pp.currency_code,
            price=float(pp.price),
            is_active=pp.is_active,
            created_at=pp.created_at,
            updated_at=pp.updated_at,
        )

    @staticmethod
    def delete_price(db: Session, product_id: str, price_id: str) -> None:
        pp = (
            db.query(ProductPrice)
            .filter(ProductPrice.id == price_id, ProductPrice.product_id == product_id)
            .first()
        )
        if not pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price record '{price_id}' for product '{product_id}' not found.",
            )
        db.delete(pp)
        db.commit()
