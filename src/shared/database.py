"""
Database configuration and connection management.
"""

import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base

from .config import get_config

# Create Base class for models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize database manager with configuration."""
        self.config = config or get_config()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._setup_engine()
    
    def _setup_engine(self) -> None:
        """Set up the database engine based on configuration."""
        database_url = self._get_database_url()
        
        # Engine configuration
        engine_kwargs = {
            "echo": self.config.get("database", {}).get("echo", False),
            "future": True,
        }
        
        # SQLite-specific configuration
        if database_url.startswith("sqlite"):
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            })
        
        self.engine = create_engine(database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def _get_database_url(self) -> str:
        """Get database URL from configuration."""
        db_config = self.config.get("database", {})
        
        # Production PostgreSQL
        if db_config.get("type") == "postgresql":
            host = db_config.get("host", "localhost")
            port = db_config.get("port", 5432)
            database = db_config.get("database", "crypto_tax_calc")
            username = db_config.get("username", "postgres")
            password = db_config.get("password", "")
            
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        # Development SQLite (default)
        db_path = db_config.get("path", "data/crypto_tax_calc.db")
        return f"sqlite:///{db_path}"
    
    def get_session(self) -> Session:
        """Get a database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        
        # Create tables using Base metadata
        # Note: Models will be implemented in Phase 3.3
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all database tables."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        
        # Note: Models will be implemented in Phase 3.3
        Base.metadata.drop_all(bind=self.engine)
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_session() -> Session:
    """Get a database session."""
    return get_database_manager().get_session()


def init_database() -> None:
    """Initialize the database with tables."""
    manager = get_database_manager()
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create tables
    manager.create_tables()
    print("✅ Database initialized successfully")


def reset_database() -> None:
    """Reset the database (drop and recreate all tables)."""
    manager = get_database_manager()
    manager.drop_tables()
    manager.create_tables()
    print("✅ Database reset successfully")
