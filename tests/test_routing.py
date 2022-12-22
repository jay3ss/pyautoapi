import pysqliteapi.routing as rt


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
    assert rt.create_path_name(["this", "is", "my", "path", "{variable: type}"]) == "/this/is/my/path/{variable:type}"


# def test_create_route():
#     from typing import Any
#     path_params = {"table": "str"}
#     def query_func(p):
#         return p
#     methods = ["GET"]
#     path_params = {"column": "str", "conditional": "str", "value": "Any"}
#     route = rt.create_route(path_params, query_func, methods)
#     print(route)


if __name__ == "__main__":
    path_params = ["table1", "id"]
    function_params = {"table": "str", "column": "str"}
    def query_func(p):
        return p
    methods = ["GET"]
    query_params = {"conditional": "str", "value": "int"}
    route = rt.create_route(
        path_params,
        function_params,
        query_func,
        methods,
        query_params
    )
    print(route)
