import types


def compile_function(function_def: str) -> types.FunctionType:
    """Compiles the given function definition (str) into a callable function

    Args:
        function_def (str): the function definition

    Returns:
        types.FunctionType: the compiled function
    """
    # adapted from:
    # https://stackoverflow.com/a/48760395/3562890
    namespace = {}
    exec(function_def, namespace)
    keys = set(namespace.keys())
    keys.remove("__builtins__")
    return namespace[keys.pop()]