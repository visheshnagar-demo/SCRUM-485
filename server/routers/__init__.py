from server.routers.currencies import router as currencies_router
from server.routers.products import router as products_router
from server.routers.auth import router as auth_router
from server.routers.health import router as health_router

__all__ = ["currencies_router", "products_router", "auth_router", "health_router"]
