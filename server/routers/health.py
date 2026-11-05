from fastapi import APIRouter
from server.config import settings

router = APIRouter(tags=["Health & Status"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
