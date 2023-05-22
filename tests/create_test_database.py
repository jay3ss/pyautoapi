"""Create the test database."""
import pathlib
import sqlite3


parent = pathlib.Path(__file__).parent


def create_test_database(fname="test.db") -> None:
    """
    Creates the test database with the given name and populates it with two
    tables (table1, table2).
    """
    path = parent.parent
    conn = sqlite3.connect(path / "data" / fname)
    with conn:
        with open(path / "data/table1.sql") as f:
            conn.executescript(f.read())

        with open(path / "data/table2.sql") as f:
            conn.executescript(f.read())


if __name__ == "__main__":
    create_test_database()
