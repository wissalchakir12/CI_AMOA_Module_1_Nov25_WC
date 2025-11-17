"""
FastAPI main application for CIMR Claims Automation v1
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from src.config import settings
from src.utils.airtable_client import airtable_client
from src.api.routes import claims, classification, priority, resolution, status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CIMR Claims Automation v1 API...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"API running on {settings.api_host}:{settings.api_port}")
    
    # Test Airtable connection
    try:
        test_records = airtable_client.list_records(max_records=1)
        logger.info("✅ Airtable connection successful")
    except Exception as e:
        logger.error(f"❌ Airtable connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CIMR Claims Automation v1 API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered claims automation system for CIMR",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production"
    }


# Test Airtable connection endpoint
@app.get("/test-airtable")
async def test_airtable():
    """Test Airtable connection"""
    try:
        records = airtable_client.list_records(max_records=5)
        return {
            "success": True,
            "message": "Airtable connection successful",
            "record_count": len(records)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Airtable connection failed: {str(e)}"
        }


# Include API routes
app.include_router(claims.router, prefix="/api/claims", tags=["claims"])
app.include_router(classification.router, prefix="/api/classify", tags=["classification"])
app.include_router(priority.router, prefix="/api/score", tags=["priority"])
app.include_router(resolution.router, prefix="/api/generate_draft", tags=["resolution"])
app.include_router(status.router, prefix="/api/status", tags=["status"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if settings.debug else "Contact support for assistance."
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
