# DBSession object; manages connections
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.core.config import settings
from app.core.logger import get_module_logger
from app.db import models #to create tables if neccecesary
from logging import Logger

MAX_RETRIES=3
WAIT_SECONDS=2

logger = get_module_logger(__name__)


for attempt in range(1, MAX_RETRIES + 1):
    try:
        logger.info(f"Attempt {attempt}/{MAX_RETRIES}: connecting to database...")
        engine = create_engine(settings.database_url, echo=False)

        logger.info(f"Connecting to: {settings.database_url}")
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful.")
        break
    except OperationalError as e:
        logger.warning(f"❌ Database not ready ({e}); retrying in {WAIT_SECONDS}s...")
        time.sleep(WAIT_SECONDS)
else:
    raise RuntimeError(f"❌ Could not connect to the database after {MAX_RETRIES} attempts.")

# engine = create_engine(settings.database_url, echo=False)
Base.metadata.create_all(engine) #create tables if it doesn't exist

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# for fastapi injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()