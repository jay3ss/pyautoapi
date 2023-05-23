import pathlib
from dataclasses import dataclass
from typing import Union

import sqlalchemy as sa
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.routing import APIRoute
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


Database = Union[str, sa.Engine, URL]


class PyAutoAPI(FastAPI):
    def __init__(
        self,
        database: Database = None,
        debug: bool = False,
        title: str = "PyAutoAPI",
        description: str = "",
        version: str = "0.0.2",
        **kwargs: dict,
    ) -> None:
        super().__init__(
            debug=debug,
            routes=None,
            title=title,
            description=description,
            version=version,
            **kwargs,
        )
        if database:
            self.init_api(database=database)

    def init_api(
            self,
            database: Database = None,
            **kwargs: dict
        ) -> None:
        """
        Initialize the app.

        Args:
            db_url (UrlLike): a string or URL to connect to the database
            kwargs (dict): key words arguments for SQLAlchemy's `sessionmaker`.
        """
        query = Query(database=database, **kwargs)
        route = Route(query=query)
        self.router.add_api_route(
            path=route.path, endpoint=route.endpoint, methods=route.methods
        )


class Route(APIRoute):
    def __init__(
        self,
        query: "Query",
        path: str = "/",
        methods: list = None
    ) -> None:
        if not methods:
            methods = ["get", "post"]
        self._query = query
        super().__init__(path=path, endpoint=self.endpoint, methods=methods)

    async def endpoint(self, statement: str) -> Response:
        results = self._query.execute(statement)
        if not results:
            status_code = status.HTTP_400_BAD_REQUEST
            detail = f"Invalid statement: {results.error}"
            return HTTPException(status_code=status_code, detail=detail)

        return results.results


class Query:
    """Object to query the database."""

    def __init__(self, database: Database, **kwargs) -> None:
        if isinstance(database, (str, URL)):
            engine = sa.create_engine(database)
        elif isinstance(database, sa.Engine):
            engine = database
        else:
            msg = ("Invalid type for 'database' parameter. Expected str, "
                   f"Engine, or URL, but received {type(database)}.")
            raise TypeError(msg)
        self._Session = sessionmaker(bind=engine, **kwargs)

    def execute(self, query: str) -> "Results":
        """Runs the given query on the database

        Args:
            query (str): the SQL query to execute

        Returns:
            Lists: returns the results of the query
        """
        statement = sa.text(query)
        with self._Session() as session:
            try:
                # the mappings method allows us to get the result in
                # a list of dicts
                res = session.execute(statement).mappings().all()
                results = Results(results=res, successful=True)
            except (sa.exc.OperationalError, sa.exc.IntegrityError) as e:
                # TODO: implement logging
                # for now, just print the error.
                print(e, flush=True)
                results = Results(error=e)
            except sa.exc.ResourceClosedError as e:
                # if we're here we're probably trying to:
                # insert, update, or delete -> don't receive results
                # from executing statement
                session.execute(statement)
                res = [{"info": "Statement executed successfully"}]
                results = Results(results=res, successful=True)
        return results


@dataclass
class Results:
    """
    Holds the results of executing a database statement
    """
    results: list[dict] = None
    successful: bool = False
    error: str = None

    def __bool__(self) -> bool:
        return self.successful
