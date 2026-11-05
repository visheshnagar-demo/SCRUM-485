import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.database import init_db, seed_data, SessionLocal
from server.routers.currencies import router as currencies_router
from server.routers.products import router as products_router
from server.routers.exchange_rates import router as exchange_rates_router
from server.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema & seed initial data on application startup
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Product Catalog & Multi-Currency Pricing Service",
    description="Multi-currency catalog pricing engine with ISO 4217 validation, explicit product price matrices, and exchange rate conversion fallback.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware for full-stack integration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(currencies_router)
app.include_router(products_router)
app.include_router(exchange_rates_router)
app.include_router(auth_router)


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "product-catalog-currency-service",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server.main:app", host="0.0.0.0", port=port, reload=True)
