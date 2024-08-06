import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.utils.settings import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.ECHO_SQL,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    future=True,
)
