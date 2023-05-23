import pathlib
from dataclasses import dataclass
from typing import TypeVar

import sqlalchemy as sa
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.routing import APIRoute
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


# adapted from @maf88's comment on:
# https://stackoverflow.com/a/58541858
UrlLike = TypeVar("UrlLike", str, URL)


class PyAutoAPI(FastAPI):
    def __init__(
        self,
        db_url: UrlLike = None,
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
        if db_url:
            self.init_api(db_url=db_url)

    def init_api(
            self,
            db_url: UrlLike,
            **kwargs: dict
        ) -> None:
        """
        Initialize the app.

        Args:
            db_url (UrlLike): a string or URL to connect to the database
            kwargs (dict): key words arguments for SQLAlchemy's `sessionmaker`.
        """
        query = Query(db_url=db_url, **kwargs)
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
    """Object to query the database.

    NOTE: currently only supports the R in CRUD
    """

    def __init__(self, db_url: UrlLike, **sa_kwargs) -> None:
        engine = sa.create_engine(db_url)
        self._Session = sessionmaker(bind=engine, **sa_kwargs)

    def execute(self, query: str) -> "Results":
        """Runs the given query on the database

        Args:
            query (str): the SQL query to execute

        Returns:
            Lists: returns the results of the query
        """
        statement = sa.text(query)
        # with Session(self._session) as session:
        with self._Session() as session:
            # with conn.begin():
            #     statement = sa.text(query)
            #     try:
            #         # the mappings method allows us to get the result in
            #         # a list of dicts
            #         res = conn.execute(statement).mappings().all()
            #         results = Results(results=res, successful=True)
            #     except (sa.exc.OperationalError, sa.exc.IntegrityError) as e:
            #         # TODO: implement logging
            #         # for now, just print the error.
            #         print(e, flush=True)
            #         results = Results(error=e)
            #     except sa.exc.ResourceClosedError as e:
            #         try:
            #             # if we're here we're probably trying to:
            #             # insert, update, or delete -> need to commit
            #             conn.execute(statement)
            #             # session.commit()
            #             res = [{"info": "Statement executed successfully"}]
            #             results = Results(results=res, successful=True)
            #         except Exception as e:
            #             print(e, flush=True)
            #             results = Results(error=e)
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
                try:
                    # if we're here we're probably trying to:
                    # insert, update, or delete -> need to commit
                    session.execute(statement)
                    # session.commit()
                    res = [{"info": "Statement executed successfully"}]
                    results = Results(results=res, successful=True)
                except Exception as e:
                    print(e, flush=True)
                    results = Results(error=e)
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


import uvicorn
api = PyAutoAPI(debug=True)


if __name__ == "__main__":
    # import argparse
    import uvicorn

    # parser = argparse.ArgumentParser(description="Automatic API")
    # parser.add_argument("--db", action="store", dest="db", help="Path to the database file")
    # results = parser.parse_args()

    # api.init_api(results.db)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    url = f'sqlite:///{str(pathlib.Path("test.db"))}'

    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        api.init_api(db_url=url)
        uvicorn.run(api)
