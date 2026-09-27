from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
from sqlalchemy import create_engine, text
from app.core.config import settings

from app.api.sources import router as sources_router
from app.api.mappings import router as mappings_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS setup for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(sources_router, prefix=settings.API_V1_STR)
app.include_router(mappings_router, prefix=settings.API_V1_STR)



@app.get("/")
def read_root():
    return {"message": "Entity Resolution API is running"}

@app.get("/health")
def check_health():
    # 1. Test PostgreSQL DB connectivity
    db_status = "disconnected"
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Test Redis connectivity
    redis_status = "disconnected"
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        if r.ping():
            redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "api": "connected",
        "database": db_status,
        "redis": redis_status,
    }
