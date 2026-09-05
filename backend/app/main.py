import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.seed import seed_demo_data

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.plans import router as plans_router
from app.api.v1.gmail import router as gmail_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.mobile import router as mobile_router
from app.api.v1.documents import router as docs_router
from app.api.v1.ai import router as ai_router
from app.api.v1.news import router as news_router
from app.api.v1.insights import router as insights_router
from app.api.v1.settings import router as settings_router
from app.api.v1.audit import router as audit_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pulse.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    if settings.ENVIRONMENT == "development":
        logger.info("Development environment detected: Seeding demo dataset...")
        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)
    else:
        logger.info("Production environment detected: Demo seeding disabled. Awaiting live user data.")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred while processing the request."}
    )

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(plans_router, prefix=settings.API_V1_STR)
app.include_router(gmail_router, prefix=settings.API_V1_STR)
app.include_router(calendar_router, prefix=settings.API_V1_STR)
app.include_router(mobile_router, prefix=settings.API_V1_STR)
app.include_router(docs_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(news_router, prefix=settings.API_V1_STR)
app.include_router(insights_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)

@app.get("/")
@app.get("/health")
async def root():
    return {
        "app": "PULSE AI Backend",
        "tagline": "Everything important in your digital life. One intelligent plan for your day.",
        "status": "ONLINE",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
