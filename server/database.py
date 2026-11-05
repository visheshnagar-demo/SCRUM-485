import os
import uuid
from datetime import datetime, timezone
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalog.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    # Truncate to 72 bytes for bcrypt compatibility
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def init_db(target_engine=None):
    from server.models import Currency, Product, ProductPrice, ExchangeRate, User  # noqa: F401

    bind_engine = target_engine or engine
    Base.metadata.create_all(bind=bind_engine)


def seed_data(db: Session):
    from server.models import Currency, Product, ProductPrice, ExchangeRate, User

    # 1. Seed Currencies
    default_currencies = [
        {
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "is_base": True,
            "is_active": True,
        },
        {
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "is_base": False,
            "is_active": True,
        },
        {
            "code": "GBP",
            "name": "British Pound",
            "symbol": "£",
            "is_base": False,
            "is_active": True,
        },
        {
            "code": "JPY",
            "name": "Japanese Yen",
            "symbol": "¥",
            "is_base": False,
            "is_active": True,
        },
        {
            "code": "CAD",
            "name": "Canadian Dollar",
            "symbol": "C$",
            "is_base": False,
            "is_active": True,
        },
    ]

    for curr_data in default_currencies:
        existing = db.query(Currency).filter(Currency.code == curr_data["code"]).first()
        if not existing:
            curr = Currency(
                id=str(uuid.uuid4()),
                code=curr_data["code"],
                name=curr_data["name"],
                symbol=curr_data["symbol"],
                is_base=curr_data["is_base"],
                is_active=curr_data["is_active"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            try:
                db.add(curr)
                db.commit()
            except IntegrityError:
                db.rollback()

    # 2. Seed Exchange Rates
    default_rates = [
        {"from_currency": "USD", "to_currency": "EUR", "rate": 0.925},
        {"from_currency": "USD", "to_currency": "GBP", "rate": 0.800},
        {"from_currency": "USD", "to_currency": "JPY", "rate": 152.00},
        {"from_currency": "USD", "to_currency": "CAD", "rate": 1.365},
    ]

    for rate_data in default_rates:
        existing = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency == rate_data["from_currency"],
                ExchangeRate.to_currency == rate_data["to_currency"],
            )
            .first()
        )
        if not existing:
            rate = ExchangeRate(
                id=str(uuid.uuid4()),
                from_currency=rate_data["from_currency"],
                to_currency=rate_data["to_currency"],
                rate=rate_data["rate"],
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            try:
                db.add(rate)
                db.commit()
            except IntegrityError:
                db.rollback()

    # 3. Seed Products and Prices
    sample_products = [
        {
            "id": "prod-8832",
            "name": "Wireless Headphones",
            "description": "Premium over-ear wireless headphones with hybrid active noise cancelling and spatial audio.",
            "category": "Audio",
            "sku": "WH-8832",
            "rating": 4.9,
            "reviews_count": 428,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 149.99, "is_active": True},
                {"currency_code": "EUR", "price": 139.99, "is_active": True},
                {"currency_code": "GBP", "price": 119.99, "is_active": True},
            ],
        },
        {
            "id": "prod-8833",
            "name": "Smartwatch",
            "description": "Next-gen smartwatch with AMOLED display, health metrics, and dual GPS.",
            "category": "Wearables",
            "sku": "SW-8833",
            "rating": 4.8,
            "reviews_count": 280,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 249.99, "is_active": True},
            ],
        },
        {
            "id": "prod-8834",
            "name": "Portable Speaker",
            "description": "Rugged IPX7 waterproof Bluetooth speaker with 360-degree immersive sound.",
            "category": "Audio",
            "sku": "PS-8834",
            "rating": 4.7,
            "reviews_count": 194,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 79.99, "is_active": True},
            ],
        },
        {
            "id": "prod-8835",
            "name": "Studio Earbuds Pro",
            "description": "Compact wireless earbuds with adaptive ANC and studio acoustic drivers.",
            "category": "Audio",
            "sku": "EP-8835",
            "rating": 4.9,
            "reviews_count": 312,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 119.99, "is_active": True},
            ],
        },
        {
            "id": "prod-8836",
            "name": "Wireless Charging Dock",
            "description": "Qi2 15W high-speed multi-device charging stand for phone and accessories.",
            "category": "Accessories",
            "sku": "WC-8836",
            "rating": 4.6,
            "reviews_count": 150,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 49.99, "is_active": True},
            ],
        },
        {
            "id": "prod-8837",
            "name": "Hi-Fi Audio DAC Amplifier",
            "description": "Reference-grade 32-bit / 768kHz digital-to-analog converter and headphone amplifier.",
            "category": "Audio",
            "sku": "DAC-8837",
            "rating": 4.9,
            "reviews_count": 89,
            "in_stock": True,
            "prices": [
                {"currency_code": "USD", "price": 189.99, "is_active": True},
            ],
        },
    ]

    for p_data in sample_products:
        prod = db.query(Product).filter(Product.id == p_data["id"]).first()
        if not prod:
            prod = Product(
                id=p_data["id"],
                name=p_data["name"],
                description=p_data["description"],
                category=p_data["category"],
                sku=p_data["sku"],
                rating=p_data["rating"],
                reviews_count=p_data["reviews_count"],
                in_stock=p_data["in_stock"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            try:
                db.add(prod)
                db.commit()
            except IntegrityError:
                db.rollback()

        for price_data in p_data["prices"]:
            existing_price = (
                db.query(ProductPrice)
                .filter(
                    ProductPrice.product_id == p_data["id"],
                    ProductPrice.currency_code == price_data["currency_code"],
                )
                .first()
            )
            if not existing_price:
                pp = ProductPrice(
                    id=str(uuid.uuid4()),
                    product_id=p_data["id"],
                    currency_code=price_data["currency_code"],
                    price=price_data["price"],
                    is_active=price_data["is_active"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                try:
                    db.add(pp)
                    db.commit()
                except IntegrityError:
                    db.rollback()

    # 4. Seed Test Users
    test_users = [
        {
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "role": "user",
        },
        {
            "email": "admin@example.com",
            "password": "adminpassword",
            "full_name": "Admin User",
            "role": "admin",
        },
    ]

    for u_data in test_users:
        existing_u = db.query(User).filter(User.email == u_data["email"]).first()
        if not existing_u:
            user = User(
                id=str(uuid.uuid4()),
                email=u_data["email"],
                hashed_password=hash_password(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            try:
                db.add(user)
                db.commit()
            except IntegrityError:
                db.rollback()
