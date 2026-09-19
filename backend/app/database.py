from functools import lru_cache

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from app.config import database_path


@lru_cache
def get_engine():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        URL.create("sqlite", database=str(path)),
        connect_args={"check_same_thread": False, "timeout": 10},
    )


def get_session():
    with Session(get_engine()) as session:
        yield session
