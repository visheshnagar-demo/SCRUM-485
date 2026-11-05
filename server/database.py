import uuid
from decimal import Decimal
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from server.config import settings

Base = declarative_base()

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def init_db(custom_engine=None):
    from server.models.currency import Currency, ExchangeRate  # noqa: F401
    from server.models.product import Product, ProductPrice  # noqa: F401
    from server.models.user import User  # noqa: F401

    target_engine = custom_engine or engine
    Base.metadata.create_all(bind=target_engine)


def seed_data(db: Session):
    from server.models.currency import Currency, ExchangeRate
    from server.models.product import Product, ProductPrice
    from server.models.user import User

    # 1. Seed Users (Test and Admin)
    users_to_seed = [
        {
            "email": "test@example.com",
            "password": "testpassword",
            "role": "user",
        },
        {
            "email": "admin@example.com",
            "password": "adminpassword",
            "role": "admin",
        },
    ]
    for u_data in users_to_seed:
        existing = db.query(User).filter(User.email == u_data["email"]).first()
        if not existing:
            new_user = User(
                id=str(uuid.uuid4()),
                email=u_data["email"],
                hashed_password=hash_password(u_data["password"]),
                role=u_data["role"],
                is_active=True,
                is_verified=True,
            )
            db.add(new_user)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()

    # 2. Seed Supported Currencies (USD, EUR, GBP, JPY, CAD)
    currencies_to_seed = [
        {"code": "USD", "symbol": "$", "is_base": True, "is_active": True},
        {"code": "EUR", "symbol": "€", "is_base": False, "is_active": True},
        {"code": "GBP", "symbol": "£", "is_base": False, "is_active": True},
        {"code": "JPY", "symbol": "¥", "is_base": False, "is_active": True},
        {"code": "CAD", "symbol": "C$", "is_base": False, "is_active": True},
    ]
    for c_data in currencies_to_seed:
        existing = db.query(Currency).filter(Currency.code == c_data["code"]).first()
        if not existing:
            new_curr = Currency(
                id=str(uuid.uuid4()),
                code=c_data["code"],
                symbol=c_data["symbol"],
                is_base=c_data["is_base"],
                is_active=c_data["is_active"],
            )
            db.add(new_curr)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()

    # 3. Seed Exchange Rates from USD
    rates_to_seed = [
        {
            "from_currency_code": "USD",
            "to_currency_code": "EUR",
            "rate": Decimal("0.925000"),
        },
        {
            "from_currency_code": "USD",
            "to_currency_code": "GBP",
            "rate": Decimal("0.800000"),
        },
        {
            "from_currency_code": "USD",
            "to_currency_code": "JPY",
            "rate": Decimal("152.000000"),
        },
        {
            "from_currency_code": "USD",
            "to_currency_code": "CAD",
            "rate": Decimal("1.350000"),
        },
        {
            "from_currency_code": "USD",
            "to_currency_code": "USD",
            "rate": Decimal("1.000000"),
        },
    ]
    for r_data in rates_to_seed:
        existing = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency_code == r_data["from_currency_code"],
                ExchangeRate.to_currency_code == r_data["to_currency_code"],
            )
            .first()
        )
        if not existing:
            new_rate = ExchangeRate(
                id=str(uuid.uuid4()),
                from_currency_code=r_data["from_currency_code"],
                to_currency_code=r_data["to_currency_code"],
                rate=r_data["rate"],
                is_active=True,
            )
            db.add(new_rate)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()

    # 4. Seed Products & Explicit Pricing Matrices
    # Sample product prod-8832 ("Wireless Headphones")
    headphones = db.query(Product).filter(Product.name == "Wireless Headphones").first()
    if not headphones:
        headphones = Product(
            id="prod-8832",
            name="Wireless Headphones",
            description="Over-ear high fidelity with Active Noise Cancellation (ANC)",
            category="Audio & Wearables",
            base_price=Decimal("149.99"),
            base_currency_code="USD",
            is_active=True,
            rating=Decimal("4.9"),
            reviews_count=428,
        )
        db.add(headphones)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            headphones = (
                db.query(Product).filter(Product.name == "Wireless Headphones").first()
            )

    if headphones:
        # Explicit EUR and GBP prices for prod-8832
        explicit_prices = [
            {
                "product_id": headphones.id,
                "currency_code": "USD",
                "price": Decimal("149.99"),
                "is_active": True,
            },
            {
                "product_id": headphones.id,
                "currency_code": "EUR",
                "price": Decimal("139.99"),
                "is_active": True,
            },
            {
                "product_id": headphones.id,
                "currency_code": "GBP",
                "price": Decimal("119.99"),
                "is_active": True,
            },
        ]
        for p_data in explicit_prices:
            existing_p = (
                db.query(ProductPrice)
                .filter(
                    ProductPrice.product_id == p_data["product_id"],
                    ProductPrice.currency_code == p_data["currency_code"],
                )
                .first()
            )
            if not existing_p:
                new_price = ProductPrice(
                    id=str(uuid.uuid4()),
                    product_id=p_data["product_id"],
                    currency_code=p_data["currency_code"],
                    price=p_data["price"],
                    is_active=p_data["is_active"],
                )
                db.add(new_price)
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()

    # Additional standard products from design spec
    other_products = [
        {
            "id": "prod-1001",
            "name": "Smartwatch",
            "description": "AMOLED display, Dual GPS smartwatch",
            "category": "Wearables",
            "base_price": Decimal("249.99"),
            "rating": Decimal("4.8"),
            "reviews_count": 280,
        },
        {
            "id": "prod-1002",
            "name": "Portable Speaker",
            "description": "360 sound, IPX7 waterproof portable speaker",
            "category": "Audio",
            "base_price": Decimal("79.99"),
            "rating": Decimal("4.7"),
            "reviews_count": 194,
        },
        {
            "id": "prod-1003",
            "name": "Studio Earbuds Pro",
            "description": "Active Noise Cancellation studio earbuds",
            "category": "Audio",
            "base_price": Decimal("119.99"),
            "rating": Decimal("4.9"),
            "reviews_count": 312,
        },
        {
            "id": "prod-1004",
            "name": "Wireless Charging Dock",
            "description": "Qi2 15W Fast Charge wireless dock",
            "category": "Accessories",
            "base_price": Decimal("49.99"),
            "rating": Decimal("4.6"),
            "reviews_count": 150,
        },
        {
            "id": "prod-1005",
            "name": "Hi-Fi Audio DAC Amplifier",
            "description": "32-bit / 768kHz reference grade DAC amplifier",
            "category": "Audio",
            "base_price": Decimal("189.99"),
            "rating": Decimal("4.9"),
            "reviews_count": 88,
        },
    ]
    for op in other_products:
        existing = db.query(Product).filter(Product.id == op["id"]).first()
        if not existing:
            new_prod = Product(
                id=op["id"],
                name=op["name"],
                description=op["description"],
                category=op["category"],
                base_price=op["base_price"],
                base_currency_code="USD",
                is_active=True,
                rating=op["rating"],
                reviews_count=op["reviews_count"],
            )
            db.add(new_prod)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
