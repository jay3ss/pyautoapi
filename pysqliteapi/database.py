import pathlib
from typing import Any, List, TypeVar

import sqlalchemy as sa
from sqlalchemy import Float, Integer, LargeBinary, Text
from sqlalchemy.engine.base import Engine


# adapted from @maf88's comment on:
# https://stackoverflow.com/a/58541858
PathLike = TypeVar("PathLike", str, pathlib.Path, None)


def load_db(path: str|PathLike) -> Engine:
    """Returns a connection to the SQLite database

    Args:
        path (str | PathLike): the path to the database file

    Returns:
        Engine: a connection to the database
    """
    return sa.create_engine(f"sqlite:///{path}", echo=True)


def read_table_names(db: Engine) -> List[str]:
    """Returns the table names of the given database as a list of strings

    Args:
        db (Engine): connection to the database

    Returns:
        List[str]: table names
    """
    # adapted from:
    # https://stackoverflow.com/a/34570549
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    with db:
        return [name[0] for name in db.execute(query).fetchall()]


def read_column_names(db: Engine, table: str) -> List[str]:
    """Returns the column names from the given table and database

    Args:
        db (Engine): connection to the database
        table (str): table name

    Returns:
        List[str]: column names
    """
    query = "PRAGMA table_info({});".format(table)
    with db:
        return [col[1] for col in db.execute(query).fetchall()]


def read_column_names_and_types(db: Engine, table: str) -> dict:
    """Returns a dict of column names and column types as a key-value pair

    Args:
        db (Engine): connection to the database
        table (str): table name

    Returns:
        dict: column names and types as key-value pairs
    """
    type_map = {
        "INTEGER": int,
        "NULL": None,
        "REAL": float,
        "NUMERIC": float,
        "TEXT": str,
        "BLOB": bytes,
    }
    query = "PRAGMA table_info({});".format(table)
    with db:
        return {col[1]: type_map[col[2]] for col in db.execute(query).fetchall()}


def inspect(db: Engine) -> dict:
    """Inspects the given database and returns a dict of information about each
    table in the database. Each key in the dict contains a list of dicts with
    information about each column in the table such as its name, type, and if
    it's a primary key or not.

    Args:
        db (Engine): connection to the database

    Returns:
        dict: top-level keys are the table names with the values as list of dicts
        of information of each column in the table. E.g.,

            {
                "table1": [
                    {
                        "name": "id",
                        "type": Integer,
                        "primary_key": True,
                    },
                    ...
                ],
                "table2": [...],
                ...
            }
    """
    type_map = {
        "INTEGER": Integer,
        "NULL": None,
        "REAL": Float,
        "NUMERIC": Float,
        "TEXT": Text,
        "BLOB": LargeBinary,
    }
    insp = sa.inspect(db)
    columns = {
        table: [
            {
                "name": col["name"],
                "type": type_map[str(col["type"])],
                "primary_key": bool(col["primary_key"])
            }
            for col in insp.get_columns(table)
        ]
        for table in insp.get_table_names()
    }
    return columns
