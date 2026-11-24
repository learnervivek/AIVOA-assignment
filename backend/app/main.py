import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_db_connection, async_engine
from app.api.v1.api import api_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.investigations import router as investigations_router
from app.api.v1.endpoints.ai import router as ai_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pharma_rca")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI-Powered Pharma RCA Module API...")
    db_status = await check_db_connection()
    if db_status.get("status") == "connected":
        logger.info(f"Connected to PostgreSQL database: {db_status.get('database')}")
    else:
        logger.warning(f"Database connection warning: {db_status}")
    yield
    logger.info("Shutting down application and disposing DB pool...")
    await async_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Root Cause Analysis (RCA) Module for Pharmaceutical API Manufacturing (GMP / ICH Q7)",
    lifespan=lifespan,
)

# CORS configuration for React (Vite) frontend
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
# Ensure standard dev origins are present
default_dev_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
for o in default_dev_origins:
    if o not in origins:
        origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health endpoint (/health)
app.include_router(health_router)

# Direct routes matching /api/investigations specification
app.include_router(investigations_router, prefix="/api/investigations", tags=["Investigations"])

# Direct routes matching /api/ai specification
app.include_router(ai_router, prefix="/api/ai", tags=["AI RCA"])

# Versioned API routes (/api/v1/...)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "module": "AI-Powered Pharma Root Cause Analysis (RCA)",
        "docs_url": "/docs",
        "health_url": "/health",
        "investigations_url": "/api/investigations",
        "api_v1": settings.API_V1_PREFIX,
    }
