import sqlite3
from typing import List

def read_table_names(db: sqlite3.Connection) -> List[str]:
    """
    Returns the table names of the given database as a list of strings
    """
    # adapted from:
    # https://stackoverflow.com/a/34570549
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    with db:
        return [name[0] for name in db.execute(query).fetchall()]


def read_column_names(db: sqlite3.Connection, table: str) -> List[str]:
    """
    Returns the column names from the given table and database
    """
    query = "PRAGMA table_info({});".format(table)
    with db:
        return [col[1] for col in db.execute(query).fetchall()]


def read_column_names_and_types(db: sqlite3.Connection, table: str) -> List[dict]:
    """
    Returns a dict of column names and column types as a key-value pair
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
