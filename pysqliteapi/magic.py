import types


def compile_function(function_def: str, function_name: str, context: dict = None) -> types.FunctionType:
    """Compiles the given function definition (str) into a callable function

    Args:
        function_def (str): the function definition

    Returns:
        types.FunctionType: the compiled function
    """
    # adapted from:
    # https://stackoverflow.com/a/48760395
    # namespace = {}
    if not context:
        context = globals()
    exec(function_def, context)
    return context[function_name]
