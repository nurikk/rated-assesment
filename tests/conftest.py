import datetime

import pytest
from bytewax.testing import TestingSource
from starlette.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.test import getDBConfig, _init_db

from api.server import app
from models import ResourceStatisticsByDay


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


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def in_memory_db(request, event_loop):
    config = getDBConfig(app_label="models", modules=["models"])
    event_loop.run_until_complete(_init_db(config))
    request.addfinalizer(
        lambda: event_loop.run_until_complete(Tortoise._drop_databases())
    )


@pytest.fixture
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture
def db_mock(in_memory_db, event_loop):
    async def code():
        await ResourceStatisticsByDay.create(
            customer_id="cust_1",
            date=datetime.date(2024, 9, 1),
            success_requests=2,
            failed_requests=3,
            duration_mean=1.551,
            duration_p50=1.000,
            duration_p99=1.400,
        )
        await ResourceStatisticsByDay.create(
            customer_id="cust_1",
            date=datetime.date(2024, 9, 3),
            success_requests=2,
            failed_requests=3,
            duration_mean=1.551,
            duration_p50=1.000,
            duration_p99=1.400,
        )
        await ResourceStatisticsByDay.create(
            customer_id="cust_1",
            date=datetime.date(2024, 9, 5),
            success_requests=2,
            failed_requests=3,
            duration_mean=1.551,
            duration_p50=4.000,
            duration_p99=4.400,
        )


    event_loop.run_until_complete(code())
