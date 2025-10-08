"""
DDCPTS FastAPI Application Entry Point.

This is the main application file that initializes FastAPI, configures middleware,
and includes all API routes.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import time
import logging

from app.core.config import settings
from app.api.endpoints import auth, farmers, deliveries, reports, payments, stations, companies, officers
from app.core.database import engine, Base

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry (if configured)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[FastApiIntegration()],
    )
    logger.info("Sentry initialized")

# Create FastAPI app
app = FastAPI(
    title="Digital Dairy Collection & Payment Transparency System",
    description="""
    **DDCPTS API** provides comprehensive dairy collection management with:
    
    - 🥛 **Milk delivery tracking** with quality grading
    - 📱 **SMS confirmations** to farmers
    - 💰 **M-Pesa payment integration** 
    - 📊 **Analytics and reporting**
    - 🔒 **Role-based access control**
    - 📲 **Offline-first mobile support**
    
    ## Authentication
    
    Most endpoints require JWT authentication. Obtain a token via `/api/v1/auth/login`.
    
    Include the token in the `Authorization` header:
    ```
    Authorization: Bearer <your-access-token>
    ```
    
    ## Sandbox Mode
    
    All payment operations default to sandbox mode to prevent accidental real transactions.
    Set `ENABLE_REAL_PAYMENTS=true` only in production with proper approvals.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Request validation failed. Please check your input."
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred.",
            "message": "An internal server error occurred. Please try again later."
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint (liveness probe).
    
    Returns 200 OK if the service is running.
    """
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint.
    
    Verifies database connectivity and external service availability.
    """
    try:
        # Check database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "database": "connected",
            "version": "0.1.0"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(farmers.router, prefix="/api/v1/farmers", tags=["Farmers"])
app.include_router(deliveries.router, prefix="/api/v1/deliveries", tags=["Deliveries"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(stations.router, prefix="/api/v1/stations", tags=["Stations"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(officers.router, prefix="/api/v1/officers", tags=["Officers"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("DDCPTS API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create seed data if enabled
    if settings.CREATE_SEED_DATA and settings.is_development():
        logger.info("Creating seed data...")
        try:
            from app.scripts.seed_data import create_seed_data
            create_seed_data()
            logger.info("Seed data created successfully")
        except Exception as e:
            logger.error(f"Failed to create seed data: {e}", exc_info=True)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("DDCPTS API shutting down...")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint.
    
    Provides basic information and links to documentation.
    """
    return {
        "message": "Welcome to DDCPTS API",
        "version": "0.1.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "health_check": "/health",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
