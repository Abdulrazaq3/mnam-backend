import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Get database URL from environment or settings
database_url = settings.database_url

# Railway provides DATABASE_URL with postgres:// prefix, but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Handle SQLite special case for check_same_thread
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# For production, disable echo (SQL logging)
echo_sql = not settings.is_production

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=echo_sql,
    pool_pre_ping=True,  # Test connection before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
