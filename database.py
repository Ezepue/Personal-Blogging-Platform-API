import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

# Adjust engine settings based on DB type
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine
try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    logger.info("Database connected successfully.")
except Exception as e:
    logger.critical(f"Failed to connect to the database: {e}")
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
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
