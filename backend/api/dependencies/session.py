from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from core.database._session import SessionLocal
from core.utils import get_logger

logger = get_logger(__name__)


def get_session() -> Generator[sessionmaker, None, None]:
    try:
        session = SessionLocal()
        yield session
    except SQLAlchemyError as e:
        logger.exception(e)
        raise e
    finally:
        session.commit()


Session = Annotated[sessionmaker, Depends(get_session)]
