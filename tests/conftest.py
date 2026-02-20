import pytest
import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from notabene.core.database import Base, Database, init_database
from notabene.core.config import init_config, get_config

@pytest.fixture(scope="session", autouse=True)
def test_config():
    """Initialize test configuration."""
    return init_config()

@pytest.fixture(scope="function")
def test_db(tmp_path):
    """Fixture for a temporary database."""
    db_path = tmp_path / "test_notabene.db"
    db = init_database(db_path)
    yield db
    # Cleanup is handled by tmp_path

@pytest.fixture(scope="function")
def db_session(test_db):
    """Fixture for a database session."""
    with next(test_db.get_session()) as session:
        yield session

@pytest.fixture(scope="function")
def temp_storage(tmp_path):
    """Fixture for temporary file storage (PDFs, etc.)."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    return storage_dir
