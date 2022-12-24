from collections import OrderedDict
from functools import reduce
import re
from types import FunctionType
from typing import Any, Callable, Optional, TypeVar
from urllib.parse import urljoin as pathjoin

from fastapi.routing import APIRoute, APIRouter

from pysqliteapi  import magic


PathTypes = TypeVar("PathTypes", str, float, int)


class Route(APIRoute):
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827
    """

    def __init__(
        self,
        path: str,
        param_type: str,
        query_func: Callable[..., Any],
        methods: Optional[list[str]]
    ) -> None:
        self.path = None
        _, self.endpoint = create_route(path, param_type, query_func)
        super().__init__(path, endpoint=self.endpoint, methods=methods)


def create_route(
    function_params: OrderedDict[str, str],
    query_func: Callable,
    methods: list[str],
    path_params: list[str] = None,
    query_params: dict[str, str] = None,
    context: dict[str, Any] = None
) -> tuple[str, Callable]:
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827

    Args:
        path_param (str): path parameter
        path_param_type (PathTypes): path parameter type
        query_func (Callable): function to run queries

    Returns:
        tuple[str, Callable]: this returns the path (str), and endpoint function
        (Callable)
    """
    dict_str_to_args = lambda d: str(d)[1:-1].replace("'", "")
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
    args = dict_str_to_args(list(function_params.keys()))
    if query_params:
        q_params = dict_to_key_pair_brackets_strs(query_params)
        params.extend(q_params)
        q_args = dict_str_to_args(list(query_params.keys()))
        args = f"{args}, {q_args}"

    func_params = ", ".join(p.translate({ord("{"): None, ord("}"): None}) for p in params)
    func_def = (
        "async def {name}({params}):\n"
        "\treturn dict(data={query_func}({args}))"
    ).format(name=name, params=func_params, query_func=query_func.__name__, args=args)
    additional_context = {query_func.__name__: query_func}
    if context:
        additional_context.update(context)
    endpoint = magic.compile_function(func_def, name, additional_context)
    return path, endpoint


def create_args(path_params: dict[str, str], query_params: dict[str, str] = None) -> str:
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
    args = str(list(path_params.keys()))[1:-1].replace("'", "")
    if query_params:
        q_params = str(query_params)[1:-1].replace("'", "")
        params = f"{params}, {q_params}"
        q_args = str(list(query_params.keys()))[1:-1].replace("'", "")
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


class Router(APIRouter):
    """Router for the app

    adapted from:
    https://stackoverflow.com/a/70563827
    """

    def __init__(self, routes: list[Route], namespace: str = "") -> None:
        """Init method

        Args:
            params (list[dict]): list of dicts of parameter in which the
            parameter name, parameter type, the HTTP methods allowed (as a
            list), and the endpoint function are the keys. E.g.,

            [
                ...,
                {
                    "name": "param_name",
                    "type": str,
                    "methods": ["GET", "POST"],
                    "endpoint": "func",
                }
                ...,
            ]

            namespace (str, optional): The name space to be prepended to the
            route. E.g., a namespace of "myapi" and a params value of the one
            given above would result in a route of `/myapi/param_name`. Defaults
            to "", which would make the route `/param_name`.
        """
        self.namespace = namespace
        self._create_routes(routes)

    def _create_routes(self, routes: list[Route]) -> None:
        """Creates the routes"""
        for route in routes:
            self.router.add_api_route(route)


    def _create_route(self, param: dict, namespace: str = None) -> FunctionType:
        """Create a FastAPI route based on the given parameter and methods
        (optionally add a namespace)

        Args:
            param (dict): parameter in which the parameter name, parameter type,
            and the HTTP methods allowed (as a list) are the keys. E.g.,

            [
                ...,
                {"name": "param_name", "type": str, "methods": ["GET", "POST"]}
                ...,
            ]

            namespace (str, optional): The name space to be prepended to the
            route. E.g., a namespace of "myapi" and a params value of the one
            given above would result in a route of `/myapi/param_name`. Defaults
            to None, which would make the route `/param_name`.

        Returns:
            Callable: the route
        """
        # adapted from:
        # https://stackoverflow.com/a/70563827
        pass
