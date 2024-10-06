import pytest


@pytest.mark.asyncio
async def test_stats(client, sample_stats):
    response = client.get("/customers/cust_1/stats")
    assert response.status_code == 422

    response = client.get("/customers/cust_1/stats?from=aaaaa")
    assert response.status_code == 422

    response = client.get("/customers/cust_1/stats?from=2024-09-03")

    assert response.status_code == 200
    assert response.json() == [
        {
            'customer_id': 'cust_1',
            'date': '2024-09-03',
            'duration_mean': 0.3,
            'duration_p50': 0.3,
            'duration_p99': 0.3,
            'failed_requests': 3,
            'success_requests': 3,
            'uptime_percentage': 33.3
        }
    ]
