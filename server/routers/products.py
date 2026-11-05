from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.product import Product
from server.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductPriceCreate,
    ProductPriceUpdate,
    ProductPriceResponse,
    LocalizedPriceDetail,
)
from server.services.pricing_service import PricingService

router = APIRouter(tags=["Products & Pricing"])


@router.get("/products", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    currency: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List products in catalog with localized pricing based on requested currency.
    """
    return PricingService.get_products(
        db, skip=skip, limit=limit, category=category, currency_code=currency
    )


@router.post(
    "/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product in the catalog.
    """
    p = PricingService.create_product(db, product_in)
    return PricingService.get_product_by_id(db, p.id)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str, currency: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    Get single product details with localized pricing in requested currency.
    """
    prod = PricingService.get_product_by_id(db, product_id, currency_code=currency)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return prod


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str, product_in: ProductUpdate, db: Session = Depends(get_db)
):
    """
    Update product details.
    """
    p = PricingService.update_product(db, product_id, product_in)
    return PricingService.get_product_by_id(db, p.id)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Delete a product and its associated prices.
    """
    PricingService.delete_product(db, product_id)
    return None


# Product Multi-Currency Pricing Matrix Endpoints
@router.get("/products/{product_id}/prices", response_model=List[ProductPriceResponse])
def get_product_prices(product_id: str, db: Session = Depends(get_db)):
    """
    Get all explicit configured currency prices for a product.
    """
    return PricingService.get_product_prices(db, product_id)


@router.post(
    "/products/{product_id}/prices",
    response_model=ProductPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_product_price(
    product_id: str, price_in: ProductPriceCreate, db: Session = Depends(get_db)
):
    """
    Configure an explicit localized price for a product in a specific currency.
    """
    return PricingService.set_product_price(db, product_id, price_in)


@router.put(
    "/products/{product_id}/prices/{price_id_or_code}",
    response_model=ProductPriceResponse,
)
def update_product_price(
    product_id: str,
    price_id_or_code: str,
    price_in: ProductPriceUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an explicit product price entry.
    """
    return PricingService.update_product_price(
        db, product_id, price_id_or_code, price_in
    )


@router.delete(
    "/products/{product_id}/prices/{price_id_or_code}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product_price(
    product_id: str, price_id_or_code: str, db: Session = Depends(get_db)
):
    """
    Remove an explicit localized price entry for a product.
    """
    PricingService.delete_product_price(db, product_id, price_id_or_code)
    return None


@router.get("/products/{product_id}/price", response_model=LocalizedPriceDetail)
def get_localized_product_price(
    product_id: str,
    currency_code: Optional[str] = Query(
        None, description="ISO 4217 Currency Code to calculate price for"
    ),
    db: Session = Depends(get_db),
):
    """
    Calculate and return the dynamic or explicit localized price for a product.
    Falls back to exchange rate conversion or Primary Base Currency.
    """
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return PricingService.calculate_localized_price(db, p, currency_code)
