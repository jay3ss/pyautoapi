import types

from pysqliteapi import magic


def test_compiling_function():
    function_definition = """
def foo(x, y=2):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition, "foo")
    assert type(func) == types.FunctionType
    assert func(2, 3) == 81


def test_type_annotations_of_compiled_function():
    function_definition = """
def foo(x: int, y: float):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition, "foo")
    assert func.__annotations__ == {"x": int, "y": float}


def test_type_defaults_of_compiled_function():
    function_definition = """
def foo(x: int = 13, y: float = 0):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition, "foo")
    assert func.__defaults__ == (13, 0)


def test_composing_functions_within_single_string():
    function_def = """
def test_func(param):
    return param

def test_func2(param):
    data = test_func(param)
    return {"data": data}
    """
    func = magic.compile_function(function_def, "test_func2", globals())
    assert func("hello")
    assert func("hello") == {"data": "hello"}


def test_composing_functions():
    def test_func(param):
        return param

    function_def = """
def test_func2(param):
    data = test_func(param)
    return {"data": data}
    """
    func = magic.compile_function(function_def, "test_func2", globals())
    assert func("hello")
    assert func("hello") == {"data": "hello"}


if __name__ == "__main__":
    test_composing_functions()
