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


if __name__ == "__main__":
    test_compiling_function()