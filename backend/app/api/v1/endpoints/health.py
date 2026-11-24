from fastapi import APIRouter, status
from app.core.config import settings
from app.core.database import check_db_connection

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
async def health_check():
    """
    Health check endpoint that verifies server liveness and PostgreSQL connectivity.
    """
    db_health = await check_db_connection()
    is_db_connected = db_health.get("status") == "connected"

    overall_status = "healthy" if is_db_connected else "degraded"

    return {
        "status": overall_status,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "database": db_health,
    }
