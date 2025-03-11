import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/blogdb")

# Create PostgreSQL engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Ensures connections are alive before using them
        pool_size=10,        # Maintains up to 10 open connections
        max_overflow=20,     # Allows up to 20 additional temporary connections
    )
    logger.info("Database connected successfully.")
except Exception as e:
    logger.critical(f"Failed to connect to the database: {e}", exc_info=True)
    raise

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    """ Dependency function to get a database session. """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error occurred during the database session: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
