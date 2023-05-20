import pathlib
import sqlite3


def create_test_database(db_name=":memory:") -> None:
    """
    Creates the test database with the given name and populates it with two
    tables (table1, table2).
    """
    path = pathlib.Path(__file__).parent
    conn = sqlite3.connect(db_name)
    with conn:
        with open(path / "data/table1.sql") as f:
            conn.executescript(f.read())

        with open(path / "data/table2.sql") as f:
            conn.executescript(f.read())
