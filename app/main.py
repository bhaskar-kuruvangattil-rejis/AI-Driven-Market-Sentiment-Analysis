from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from contextlib import asynccontextmanager

# Import routes and utilities
from app.routes import router
from app.utils.database import test_database_connection
from app.utils.s3_handler import s3_handler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting up AI Market Sentiment Analysis API...")
    
    try:
        # Test database connection
        db_status = test_database_connection()
        if db_status:
            logger.info("Database connection: OK")
        else:
            logger.warning("Database connection: FAILED")
        
        # Test S3 connection
        s3_status = s3_handler.test_connection()
        if s3_status:
            logger.info("S3 connection: OK")
        else:
            logger.warning("S3 connection: FAILED")
        
        logger.info("Startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Market Sentiment Analysis API...")
    logger.info("Shutdown completed")


# Create FastAPI app with metadata
app = FastAPI(
    title="AI-Driven Market Sentiment Analysis",
    description="API for analyzing market sentiment using AWS Comprehend and storing results in PostgreSQL and S3",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI-Driven Market Sentiment Analysis",
        "version": "1.0.0",
        "description": "API for analyzing market sentiment using NLP",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=debug,
        log_level="info"
    )
