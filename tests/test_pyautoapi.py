import pytest


def test_execute_query(api_client):
    # Send a GET request to the test route with a query
    response = api_client.get("/?statement=SELECT * FROM table1")

    # Assert that the response is successful and contains the expected query
    assert response.status_code == 200
    assert len(response.json()) == 100


def test_invalid_query(api_client):
    # Send a POST request to the default route with an invalid query
    response = api_client.post("/", json={"statement": "INVALID QUERY"})

    # Assert that the response is a bad request
    assert response.status_code == 400


def test_query_execution(api_client):
    # Send a GET request to the test route with a query
    response = api_client.get("/?statement=SELECT * FROM table1")

    # Assert that the response is successful and contains the query results
    assert response.status_code == 200
    assert response.json()["results"] is not None


def test_query_execution_failure(api_client):
    # Send a GET request to the test route with a query
    response = api_client.get("/?statement=SELECT * FROM table1")

    # Assert that the response is a server error
    assert response.status_code == 500


if __name__ == "__main__":
    pytest.main(["-s", __file__])
