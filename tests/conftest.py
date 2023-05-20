"""
Pytest fixtures
"""
import pathlib

import pytest
import sqlalchemy as sa


base_dir = pathlib.Path(__file__).parent


@pytest.fixture
def connection():
    # create the database with sqlite and then yield a sqlalchemy connection
    engine = sa.create_engine("sqlite://")

    with engine.connect() as conn:
        with open(base_dir / "data/table1.sql") as f:
            for line in f.read().split(";"):
                conn.execute(sa.text(line + ";"))

        with open(base_dir / "data/table2.sql") as f:
            for line in f.read().split(";"):
                conn.execute(sa.text(line + ";"))

        yield conn
