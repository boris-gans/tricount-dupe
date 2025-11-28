import os
import sys
from pathlib import Path
import logging

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure required environment variables for settings are present before imports
os.environ.setdefault("database-user", "test_user")
os.environ.setdefault("database-pw", "test_pw")
os.environ.setdefault("database-name", "test_db")
os.environ.setdefault("database-url-raw", "https://google.com")

os.environ.setdefault("jwt-secret-key", "test_secret_key")
os.environ.setdefault("jwt-algorithm", "HS256")
os.environ.setdefault("jwt-expiration-minutes", "60")
os.environ.setdefault("log-format", "%(levelname)s:%(name)s:%(message)s")
os.environ.setdefault("base-logger-name", "test_app")
os.environ.setdefault("frontend_origins", "127.0.0.0:8000")




# Make sure the app package is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.db.base import Base
from app.core import config as config_module


TEST_DATABASE_URL = "sqlite:///:memory:"

# Point application settings at the in-memory SQLite database before the session
# module (which instantiates the engine) is imported.
config_module.Settings.database_url = property(lambda self: TEST_DATABASE_URL)

import app.db.session as session_module
from app.db.session import get_db
from app.core.logger import setup_logging, get_request_logger
from app.main import app


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override engine and SessionLocal used by the application
session_module.engine = engine
session_module.SessionLocal = TestingSessionLocal

Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    session.begin_nested()

    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    event.listen(session, "after_transaction_end", restart_savepoint)

    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", restart_savepoint)
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    logger = setup_logging()
    app.state.logger = logger

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_request_logger():
        return logging.getLogger("test-request")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_request_logger] = override_get_request_logger

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_header(db_session):
    from app.db.models import User
    from app.core.security import hash_password, create_access_token

    user = User(name="Test User", email="test@example.com", pw=hash_password("password123"))
    db_session.add(user)
    db_session.flush()

    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}, user
