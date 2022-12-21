import types


def compile_function(function_def: str, function_name: str) -> types.FunctionType:
    """Compiles the given function definition (str) into a callable function

    Args:
        function_def (str): the function definition

    Returns:
        types.FunctionType: the compiled function
    """
    # adapted from:
    # https://stackoverflow.com/a/48760395
    # namespace = {}
    exec(function_def, globals())
    return globals()[function_name]
