"""Database configuration and session management."""
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

# Base class for all models
Base = declarative_base()


class Database:
    """Database manager for NotaBene."""

    def __init__(self, db_path: str | Path):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False},  # Needed for SQLite
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session.

        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


# Global database instance (will be initialized by config)
_db_instance: Database | None = None


def init_database(db_path: str | Path) -> Database:
    """
    Initialize the global database instance.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Database instance
    """
    global _db_instance
    _db_instance = Database(db_path)
    _db_instance.create_tables()
    return _db_instance


def get_database() -> Database:
    """
    Get the global database instance.

    Returns:
        Database instance

    Raises:
        RuntimeError: If database not initialized
    """
    if _db_instance is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )
    return _db_instance
