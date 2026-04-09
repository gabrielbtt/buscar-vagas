from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, engine
from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db_session:
        yield db_session


@pytest.fixture(autouse=True)
def reset_sqlite_file_db():
    db_path = Path("jobs.db")
    engine.dispose()
    if db_path.exists():
        db_path.unlink()
    yield
    engine.dispose()
    if db_path.exists():
        db_path.unlink()
