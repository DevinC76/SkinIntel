import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import supabase
from app.models import AuthRequest
from app.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/signup")
@limiter.limit("5/minute")
async def signup(request: Request, auth_request: AuthRequest):
    """Register a new user"""
    try:
        response = supabase.auth.sign_up({
            "email": auth_request.email,
            "password": auth_request.password
        })

        if response.user:
            logger.info(f"New user registered: {auth_request.email}")
            return {
                "message": "User created successfully. Please check your email to verify your account.",
                "user_id": response.user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, auth_request: AuthRequest):
    """Login and get access token"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_request.email,
            "password": auth_request.password
        })

        if response.session:
            logger.info(f"User logged in: {auth_request.email}")
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": response.session.expires_in,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    """Logout current user"""
    try:
        supabase.auth.sign_out()
        logger.info(f"User logged out: {user.email}")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_token(request: Request, refresh_token: str):
    """Refresh access token"""
    try:
        response = supabase.auth.refresh_session(refresh_token)

        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": response.session.expires_in
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")
