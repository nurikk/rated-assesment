def test_stats(test_client, db_mock):
    response = test_client.get("/customers/cust_1/stats?from=2021-01-01")

    assert response.status_code == 200
