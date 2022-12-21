import pysqliteapi.routing as rt


def test_create_endpoint_name():
    path = "/this/is/my/path"
    methods = ["GET", "POST"]
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path"
    methods = ["get", "post"]
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path"
    path = "this/is/my/path/"
    assert rt.create_endpoint_name(path, methods) == "get_post_this_is_my_path"
    path = "/this/is/my/path/"


def test_create_path_name():
    pass
