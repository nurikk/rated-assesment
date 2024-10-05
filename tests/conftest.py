import datetime
import os
from typing import Generator, Any

import pytest
from bytewax.testing import TestingSource
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.server import get_application
from common import db
from models import Base, ResourceStatisticsByDay
from sqlalchemy import insert


@pytest.fixture
def test_source():
    return TestingSource([
        '2024-09-01 02:59:35 cust_1 /api/v1/resource4 404 1.551',
        '2024-09-01 18:23:20 cust_2 /api/v1/resource2 201 0.869',
        '2024-09-02 14:17:43 cust_2 /api/v1/resource2 404 1.530',
        '2024-09-05 20:58:45 cust_1 /api/v1/resource1 201 0.293',
        'abc 20:58:45 corrupted /api/v1/resource1 200 0.293',
        '2024-09-05 20:58:45 corrupted /api/v1/resource1 abc 0.293',
        '2024-09-05 20:58:45 corrupted /api/v1/resource1 100 abc',
        'corrupted line',
        '',
        None,
        '2024-09-05 16:10:17 cust_1 /api/v1/resource1 200 0.651',
        '2024-09-05 18:15:32 cust_1 /api/v1/resource3 403 0.968',
        '2024-09-01 12:31:26 cust_1 /api/v1/resource3 500 0.899',
        '2024-09-10 07:37:24 cust_2 /api/v1/resource4 403 0.296',
        '2024-09-10 06:37:54 cust_2 /api/v1/resource4 500 0.284'
    ])


# Default to using sqlite in memory for fast tests.
# Can be overridden by environment variable for testing in CI against other
# database engines
SQLALCHEMY_DATABASE_URL = os.getenv('TEST_DATABASE_URL', "sqlite://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    _app = get_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[db.get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_stats(db_session: Session):
    # insert some sample data
    db_session.execute(
        insert(ResourceStatisticsByDay).values([
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 1),
                'success_requests': 1,
                'failed_requests': 1,
                'duration_mean': 0.1,
                'duration_p50': 0.1,
                'duration_p99': 0.1,
            },
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 2),
                'success_requests': 2,
                'failed_requests': 2,
                'duration_mean': 0.2,
                'duration_p50': 0.2,
                'duration_p99': 0.2,
            },
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 3),
                'success_requests': 3,
                'failed_requests': 3,
                'duration_mean': 0.3,
                'duration_p50': 0.3,
                'duration_p99': 0.3,
            }
        ])
    )
