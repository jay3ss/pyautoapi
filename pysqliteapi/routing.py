from types import FunctionType
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from fastapi.routing import APIRoute, APIRouter


PathTypes = TypeVar("PathTypes", str, float, int)


class Route(APIRoute):
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827
    """

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Optional[List[str]]
    ) -> None:
        self.endpoint = endpoint
        super().__init__(path, endpoint=self.endpoint, methods=methods)


def create_route(
    path_param: str,
    path_type: PathTypes,
    query_func: FunctionType
) -> Tuple[str, FunctionType, List]:
    """Creates a route for the app

    adapted from:
    https://stackoverflow.com/a/70563827

    Args:
        path_param (str): _description_
        path_type (PathTypes): _description_
        query_func (FunctionType): _description_

    Returns:
        Tuple[str, FunctionType, List]: _description_
    """
    pass


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


    def _create_route(self, param: dict, namespace: str = None) -> Callable:
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
