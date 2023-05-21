import pathlib
import sqlite3
from typing import List, TypeVar

import sqlalchemy as sa
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session


# adapted from @maf88's comment on:
# https://stackoverflow.com/a/58541858
PathLike = TypeVar("PathLike", str, pathlib.Path, None)
ValueTypes = TypeVar("ValueTypes", int, str, float)


def load_db(path: str | PathLike, echo: bool = False) -> Engine:
    """Returns a connection to the SQLite database

    Args:
        path (str | PathLike): the path to the database file
        echo (bool, optional): if True, the Engine will log all statements.
        Default False.

    Returns:
        Engine: a connection to the database
    """
    return sa.create_engine(f"sqlite:///{path}", echo=echo)


class Query:
    """Object to query the database.

    NOTE: currently only supports the R in CRUD
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def execute(self, query: str) -> List:
        """Runs the given query on the database

        Args:
            query (str): the SQL query to execute

        Returns:
            Lists: returns the results of the query
        """
        with Session(self._engine) as session:
            statement = sa.text(query)
            try:
                results = session.execute(statement).mappings().all()
            except sqlite3.OperationalError as e:
                # TODO: implement logging
                # for now, just print the error.
                print(e, flush=True)


        return results
