from server.routers.currencies import router as currencies_router
from server.routers.products import router as products_router
from server.routers.exchange_rates import router as exchange_rates_router
from server.routers.auth import router as auth_router

__all__ = [
    "currencies_router",
    "products_router",
    "exchange_rates_router",
    "auth_router",
]
