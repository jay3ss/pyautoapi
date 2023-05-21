import asyncio
import pathlib

import pytest

import pyautoapi.routing as rt
import pyautoapi.database as db


@pytest.fixture
def query():
    path = pathlib.Path(__file__).parent / "data/test.db"
    engine = db.load_db(path)
    return db.Query(engine)


def test_create_endpoint_name():
    path = "/this/is/my/path"
    methods = ["GET", "POST"]
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path_endpoint"
    methods = ["get", "post"]
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path_endpoint"
    path = "this/is/my/path/"
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path_endpoint"
    path = "/this/is/my/path/"


def test_create_path_name():
    assert rt.create_path_name(["this", "is", "my", "path"]) == "/this/is/my/path"
    assert rt.create_path_name([""]) == "/"
    assert rt.create_path_name([" "]) == "/"
    assert rt.create_path_name(["this", "is", "my?", "path"]) == "/this/is/my/path"
    assert rt.create_path_name(["this", "is", "&!!!!", "path"]) == "/this/is/path"
    assert rt.create_path_name(["this", "IS", "my", "path"]) == "/this/is/my/path"
    assert rt.create_path_name(["this", "is", "my-path"]) == "/this/is/my-path"
    assert rt.create_path_name(["this", "is", "my_path"]) == "/this/is/my_path"
    # it's ok to lose the space character in the below test because this isn't
    # going to be read by humans
    assert (
        rt.create_path_name(["this", "is", "my", "path", "{variable: type}"])
        == "/this/is/my/path/{variable:type}"
    )


def test_create_route_basic(query):
    function_params = {"table": "str"}
    methods = ["GET"]
    path, endpoint = rt.create_route(function_params, query.read, methods)
    assert path == "/{table:str}"
    assert endpoint.__name__ == "get_table_str_endpoint"

    async def get_num_results():
        assert len((await endpoint("table1"))["data"]) == 100

    asyncio.run(get_num_results())


def test_create_route_query_params(query):
    function_params = {"table": "str"}
    methods = ["GET"]
    query_params = {"column": "str", "conditional": "str", "value": "int"}
    path, endpoint = rt.create_route(
        function_params, query.query, methods, query_params=query_params
    )
    assert path == "/{table:str}"

    async def get_num_results():
        assert len((await endpoint("table1", "id", "=", 1))["data"]) == 1

    asyncio.run(get_num_results())
    assert endpoint.__name__ == "get_table_str_endpoint"
