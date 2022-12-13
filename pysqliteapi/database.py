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