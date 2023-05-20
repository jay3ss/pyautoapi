from collections import OrderedDict
from functools import reduce
import re
from typing import Any, Callable
from urllib.parse import urljoin as pathjoin

from fastapi.routing import APIRoute

from pyautoapi import magic


def create_route(
    function_params: OrderedDict[str, str],
    query_func: Callable,
    methods: list[str],
    path_params: list[str] = None,
    query_params: dict[str, str] = None,
    context: dict[str, Any] = None,
) -> tuple[str, Callable]:
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827

    Args:
        function_params (OrderedDict[str, str]): parameters for the generated
        endpoint function
        query_func (Callable): the function to query the database
        methods (list[str]): HTTP methods to use (e.g., GET, POST, etc.)
        path_params (list[str], optional): extra parameters for the path. Defaults
        to None.
        query_params (dict[str, str], optional): parameters for the query, if used.
        Defaults to None.
        context (dict[str, Any], optional): Any extra context to include for
        function generation such as an extra type. Defaults to None.

    Returns:
        tuple[str, Callable]: the path (str), and endpoint function (Callable)
    """

    def dict_to_key_pair_brackets_strs(d: dict) -> list:
        return [f"{{{key}: {value}}}" for key, value in d.items()]

    if path_params:
        for_path_name_creation = path_params.copy()
        for_path_name_creation.extend(dict_to_key_pair_brackets_strs(function_params))
    else:
        for_path_name_creation = dict_to_key_pair_brackets_strs(function_params)
    path = create_path_name(for_path_name_creation)
    name = create_endpoint_name(path, methods)
    params = dict_to_key_pair_brackets_strs(function_params)
    args = _dict_str_to_args(list(function_params.keys()))
    if query_params:
        q_params = dict_to_key_pair_brackets_strs(query_params)
        params.extend(q_params)
        q_args = _dict_str_to_args(list(query_params.keys()))
        args = f"{args}, {q_args}"

    func_params = ", ".join(
        p.translate({ord("{"): None, ord("}"): None}) for p in params
    )
    func_def = (
        "async def {name}({params}):\n\treturn dict(data={query_func}({args}))"
    ).format(name=name, params=func_params, query_func=query_func.__name__, args=args)
    additional_context = {query_func.__name__: query_func}
    if context:
        additional_context.update(context)
    endpoint = magic.compile_function(func_def, name, additional_context)
    return path, endpoint


def create_args(
    path_params: dict[str, str], query_params: dict[str, str] = None
) -> str:
    """Create the arguments string for the generated function

    Args:
        path_params (dict[str, str]): Parameters that the generated function uses
        query_params (dict[str, str], optional): Query parameters for the path.
        Defaults to None.

    Returns:
        str: the prepared string of arguments and their types. E.g.,
        path_params = {"table": "str"}
        query_params = {"column": "str", "column": "str", conditional: "str", "value": "Any"}
        yields args = "table: str, column: str, column: str, conditional: str, value: Any"
    """
    args = _dict_str_to_args(path_params.keys())
    if query_params:
        q_args = _dict_str_to_args(query_params.keys())
        args = f"{args}, {q_args}"
    return args


def create_path_name(args: list[str]) -> str:
    """
    Creates a legal path from the given arguments

    Args:
        args (list[str]): list of path components

    Returns:
        str: a legal path
    """

    def clean_path(path: str) -> str:
        pattern = r"[^0-9a-zA-Z\-\_{}:]+"
        cleaned = re.sub(pattern, "", path)
        if not cleaned:
            return ""
        return f"{cleaned.lower()}/"

    # adapted from:
    # https://stackoverflow.com/a/46596076
    return "/" + reduce(pathjoin, map(clean_path, args)).rstrip("/")


def create_endpoint_name(path: str, methods: list[str]) -> str:
    """Creates the name for an endpoint given the path and methods available for
    the endpoint

    Args:
        path (str): _description_
        methods (list[str]): _description_

    Returns:
        str: _description_
    """
    parts = [method.lower() for method in methods]
    # get rid of the leading and trailing "/"s otherwise we'll get empty strings
    # which leads to a leading and trailing "_" in the function name
    parts.extend(path.lstrip("/").rstrip("/").split("/"))
    table = {ord("/"): None, ord("{"): None, ord("}"): None, ord(":"): "_"}
    return "_".join([p.translate(table) for p in parts]) + "_endpoint"


class Route(APIRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: set[str] | list[str] = None,
    ) -> None:
        super().__init__(path, endpoint, methods=methods)


def _dict_str_to_args(d: dict) -> str:
    return str(d)[1:-1].replace("'", "")
