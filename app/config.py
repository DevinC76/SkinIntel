import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
ROBOFLOW_API_KEY = os.getenv("API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    if not all([ROBOFLOW_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        logger.error("Missing required environment variables")
        raise ValueError("Missing required environment variables: API_KEY, SUPABASE_URL, SUPABASE_KEY")
    logger.info("Configuration validated successfully")

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Add your production frontend URL here
]

# Rate limiting settings
RATE_LIMIT_SIGNUP = "5/minute"
RATE_LIMIT_LOGIN = "10/minute"
RATE_LIMIT_REFRESH = "20/minute"
RATE_LIMIT_ANALYSIS = "30/minute"
RATE_LIMIT_FETCH = "60/minute"
