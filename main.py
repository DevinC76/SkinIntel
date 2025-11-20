from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import validate_config, CORS_ORIGINS, logger
from app.auth import auth_router, get_current_user
from app.analysis import analysis_router
from app.services.ml_models import model_manager

# Validate configuration on import
validate_config()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SkinIntel API...")
    model_manager.initialize()
    yield
    # Shutdown
    logger.info("Shutting down SkinIntel API...")

# Initialize FastAPI app
app = FastAPI(
    title="SkinIntel API",
    description="AI-powered skin analysis API with user authentication",
    version="2.0.0",
    lifespan=lifespan
)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(analysis_router)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "models_loaded": model_manager.is_initialized
    }

# User profile endpoint
@app.get("/me", tags=["User"])
async def get_current_user_info(user=Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
