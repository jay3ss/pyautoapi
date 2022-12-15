import types

from pysqliteapi import magic


def test_compiling_function():
    function_definition = """
def foo(x, y=2):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition)
    assert type(func) == types.FunctionType
    assert func(2, 3) == 81


def test_type_annotations_of_compiled_function():
    function_definition = """
def foo(x: int, y: float):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition)
    assert func.__annotations__ == {"x": int, "y": float}


def test_type_defaults_of_compiled_function():
    function_definition = """
def foo(x: int = 13, y: float = 0):
    z = x*y + 3
    return z**2
    """
    func = magic.compile_function(function_definition)
    assert func.__defaults__ == (13, 0)
