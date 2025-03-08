import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set! Ensure it is configured in the .env file.")
    raise ValueError("DATABASE_URL is missing!")

# Token Expiry Configuration
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
except ValueError:
    logger.error("Invalid token expiry settings. Check your .env file.")
    raise

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.critical("SECRET_KEY is missing! Set it in the .env file for security.")
    raise ValueError("SECRET_KEY is required and must be set in the .env file.")

ALGORITHM = "HS256"

# Upload Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.abspath("uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"Upload folder set to: {UPLOAD_FOLDER}")
