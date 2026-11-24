from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    investigations,
    rca,
    capa,
    ai,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(rca.router, prefix="/rca", tags=["RCA Analysis"])
api_router.include_router(capa.router, prefix="/capa", tags=["CAPA"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI RCA Workflow"])
