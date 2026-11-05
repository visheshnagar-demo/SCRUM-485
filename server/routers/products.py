from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductListResponse,
    ProductWithLocalizedPrice,
    ProductPriceCreate,
    ProductPriceUpdate,
    ProductPriceResponse,
)
from server.services.pricing_service import PricingService

router = APIRouter(prefix="/api/v1/products", tags=["Products & Pricing"])


@router.get("", response_model=ProductListResponse)
def list_products(
    currency: Optional[str] = Query(
        None, description="ISO 4217 currency code for localized prices"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(
        None, description="Search term for name/sku/description"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total, selected_curr = PricingService.list_products(
        db,
        currency_code=currency,
        category=category,
        search=search,
        skip=skip,
        limit=limit,
    )
    return ProductListResponse(
        items=items, total=total, selected_currency=selected_curr
    )


@router.post(
    "", response_model=ProductWithLocalizedPrice, status_code=status.HTTP_201_CREATED
)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    return PricingService.create_product(db, product_in)


@router.get("/{product_id}", response_model=ProductWithLocalizedPrice)
def get_product(
    product_id: str,
    currency: Optional[str] = Query(
        None, description="ISO 4217 currency code for localized price"
    ),
    db: Session = Depends(get_db),
):
    return PricingService.get_product(db, product_id, currency_code=currency)


@router.put("/{product_id}", response_model=ProductWithLocalizedPrice)
def update_product(
    product_id: str,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
):
    return PricingService.update_product(db, product_id, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    PricingService.delete_product(db, product_id)
    return None


# --- Product Pricing Matrix Endpoints ---


@router.get("/{product_id}/prices", response_model=List[ProductPriceResponse])
def get_product_prices(product_id: str, db: Session = Depends(get_db)):
    return PricingService.get_prices(db, product_id)


@router.post(
    "/{product_id}/prices",
    response_model=ProductPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
def set_product_price(
    product_id: str,
    price_in: ProductPriceCreate,
    db: Session = Depends(get_db),
):
    return PricingService.set_price(db, product_id, price_in)


@router.put("/{product_id}/prices/{price_id}", response_model=ProductPriceResponse)
def update_product_price(
    product_id: str,
    price_id: str,
    price_in: ProductPriceUpdate,
    db: Session = Depends(get_db),
):
    return PricingService.update_price(db, product_id, price_id, price_in)


@router.delete(
    "/{product_id}/prices/{price_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_product_price(
    product_id: str,
    price_id: str,
    db: Session = Depends(get_db),
):
    PricingService.delete_price(db, product_id, price_id)
    return None
