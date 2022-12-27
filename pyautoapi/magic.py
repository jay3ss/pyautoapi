"""If some magic is happening and you want to know what's doing it, this is the
place to start looking.
"""
import types


def compile_function(
    definition: str, name: str, context: dict = None
) -> types.FunctionType:
    """Compiles the given function definition (str) into a callable function

    Args:
        definition (str): the function definition

    Returns:
        types.FunctionType: the compiled function
    """
    # adapted from:
    # https://stackoverflow.com/a/48760395
    # namespace = {}
    if not context:
        context = globals()
    exec(definition, context)
    return context[name]
