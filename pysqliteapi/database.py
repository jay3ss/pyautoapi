import pathlib
from typing import TypeVar

import sqlalchemy as sa
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



