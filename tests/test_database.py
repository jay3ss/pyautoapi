import pathlib

import pytest
from sqlalchemy import create_engine

import pysqliteapi.database as db


@pytest.fixture
def load_db():
    path = pathlib.Path(__file__).parent/"data/test.db"
    return create_engine(f"sqlite:///{path}")


def test_inspect_finds_tables(load_db):
    inspect = db.inspect(load_db)
    assert list(inspect.keys()) == ["table1", "table2"]


def test_inspect_finds_column_names(load_db):
    inspect = db.inspect(load_db)
    for columns in inspect.values():
        assert [c["name"] for c in columns] == ["id", "txt", "num", "int", "rl", "blb"]


def test_inspect_finds_primary_key(load_db):
    inspect = db.inspect(load_db)
    for columns in inspect.values():
        for column in columns:
            if column["name"] == "id":
                assert column["primary_key"]
            else:
                assert not column["primary_key"]
