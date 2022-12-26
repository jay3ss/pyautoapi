import pathlib
from typing import TypeVar

from fastapi import FastAPI

import pyautoapi.database as db
import pyautoapi.routing as rt


PathLike = TypeVar("PathLike", str, pathlib.Path)


class PyAutoAPI(FastAPI):
    def __init__(
        self,
        db_path: str,
        *,
        debug: bool = False,
        title: str = "PyAutoAPI",
        description: str = "",
        version: str = "0.0.1",
    ) -> None:
        super().__init__(
            debug=debug,
            routes=None,
            title=title,
            description=description,
            version=version
        )
        routes = _create_all_routes(db_path)
        for route in routes:
            self.router.add_api_route(
                endpoint=route.endpoint, path=route.path, methods=route.methods
            )


def _create_all_routes(db_path: str) -> list[rt.Route]:
    engine = db.load_db(pathlib.Path(db_path))
    # inspector = db.inspect(engine)
    query = db.Query(engine)

    function_params = {"table": "str"}
    methods = ["GET"]
    path, endpoint = rt.create_route(function_params, query.read, methods)
    route = rt.Route(path=path, endpoint=endpoint, methods=methods)
    return [route]
