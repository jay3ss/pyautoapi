from functools import reduce
import re
from types import FunctionType
from typing import Any, Callable, List, Optional, Tuple, TypeVar
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
        methods: Optional[List[str]]
    ) -> None:
        self.path = None
        _, self.endpoint = create_route(path, param_type, query_func)
        super().__init__(path, endpoint=self.endpoint, methods=methods)


def create_route(
    path_param: str,
    path_param_type: PathTypes,
    query_func: Callable,
    methods: List[str]
) -> Tuple[str, Callable]:
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827

    Args:
        path_param (str): path parameter
        path_param_type (PathTypes): path parameter type
        query_func (Callable): function to run queries

    Returns:
        Tuple[str, Callable, List]: this returns the path (str), and endpoint
        function (Callable)
    """
    # first, we must create the magic function, then we'll be using it as our
    # endpoint
    func_def = f"""
    async def {path_param}_endpoint(path_param: {path_param_type}):
        data = {query_func}(path_param)
        return dict({path_param}=data)
    """
    context = {"query_func": query_func}
    endpoint = magic.compile_function(func_def, "", context)
    path = create_path_name(path_param)
    return path, endpoint


def create_path_name(*args) -> str:
    """Creates a legal path from the given arguments

    Returns:
        str: a legal path
    """
    def clean_path(path: str) -> str:
        pattern = "[^0-9a-zA-Z\-\_]+"
        cleaned = re.sub(pattern, "", path)
        if not cleaned:
            return ""
        return f"{cleaned.lower()}/"

    # adapted from:
    # https://stackoverflow.com/a/46596076
    return "/" + reduce(pathjoin, map(clean_path, args)).rstrip("/")


def create_endpoint_name(path: str, methods: List[str]) -> str:
    """Creates the name for an endpoint given the path and methods available for
    the endpoint

    Args:
        path (str): _description_
        methods (List[str]): _description_

    Returns:
        str: _description_
    """
    parts = [method.lower() for method in methods]
    # get rid of the leading and trailing "/"s otherwise we'll get empty strings
    # which leads to a leading and trailing "_" in the function name
    parts.extend(path.lstrip("/").rstrip("/").split("/"))
    return "_".join(parts)


class Router(APIRouter):
    """Router for the app

    adapted from:
    https://stackoverflow.com/a/70563827
    """

    def __init__(self, routes: List[Route], namespace: str = "") -> None:
        """Init method

        Args:
            params (List[dict]): list of dicts of parameter in which the
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

    def _create_routes(self, routes: List[Route]) -> None:
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
