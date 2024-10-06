from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from common.settings import get_settings

settings = get_settings()


def get_engine():
    return create_engine(str(settings.DATABASE_URL), isolation_level="AUTOCOMMIT")


def get_db() -> Session:
    engine = get_engine()
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield db
    finally:
        db.close()


DatabaseDep = Annotated[Session, Depends(get_db)]





