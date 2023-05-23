from pyautoapi import PyAutoAPI

import pytest


def test_execute_query(api_client):
    # Send a GET request to the test route with a query
    response = api_client.get("/?statement=SELECT * FROM table1")

    # Assert that the response is successful and contains the expected query
    assert response.status_code == 200
    assert len(response.json()) == 100


def test_invalid_query(api_client):
    # Send a POST request to the default route with an invalid query
    response = api_client.post("/?statement=INVALID QUERY")

    # Assert that the response is a bad request
    assert response.json()["status_code"] == 400


def test_query_non_existent_table(api_client):
    # Send a GET request to the test route with a query
    response = api_client.get("/?statement=SELECT * FROM does_not_exist")

    # Assert that the response is successful and contains the query results
    assert response.status_code == 200

    response_data = response.json()
    assert response_data is not None
    assert response_data["status_code"] == 400
    assert "Invalid statement" in response_data["detail"]


def test_valid_insert_statement(api_client):
    statement = """INSERT INTO table1(txt, num, int, rl, blb)
    VALUES ('did it work?', 3.1415927, 468, 137.0001, CAST('new blob' AS BLOB))
    """.replace(
        "\n", " "
    )
    response = api_client.post(f"/?statement={statement}")

    assert response.status_code == 200

    response_data = response.json()
    assert "status_code" not in response_data
    assert "detail" not in response_data
    assert "info" in response_data[0]


def test_invalid_insert_statement(api_client):
    # notice the missing `num` column
    statement = """INSERT INTO table1(txt, int, rl, blb)
    VALUES ('did it work?', 3.1415927, 468, 137.0001, CAST('new blob' AS BLOB))
    """.replace(
        "\n", " "
    )
    response = api_client.post(f"/?statement={statement}")

    assert response.status_code == 200

    response_data = response.json()
    assert "status_code" in response_data
    assert response_data["status_code"] == 400
    assert "detail" in response_data
    assert "Invalid statement" in response_data["detail"]


def test_using_a_url_string_no_exception(db_string_url, test_database):
    url_str = f"sqlite:///{db_string_url}"
    api = PyAutoAPI(url_str)


def test_using_incorrect_type_for_database_url(db_string_url, test_database):
    with pytest.raises(TypeError):
        api = PyAutoAPI(db_string_url)


if __name__ == "__main__":
    pytest.main(["-s", __file__])
