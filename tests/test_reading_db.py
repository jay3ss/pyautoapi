import pathlib
import sqlite3

import pytest

from pysqliteapi import database as db


parent = pathlib.Path(__file__).parent


@pytest.fixture
def test_db():
    conn = sqlite3.connect(parent/"data/test.db")
    return conn


def test_reading_tables(test_db):
    table_names = db.read_table_names(test_db)
    assert table_names == ['table1', 'table2']


def test_reading_column_names(test_db):
    table_names = db.read_table_names(test_db)
    columns = [
        db.read_column_names(test_db, name) for name in table_names
    ]
    assert columns == [
        ["id", "txt", "num", "int", "rl", "blb"],
        ["id", "txt", "num", "int", "rl", "blb"]
    ]


def test_reading_column_types(test_db):
    table_names = db.read_table_names(test_db)
    columns = [
        db.read_column_names_and_types(test_db, name) for name in table_names
    ]
    assert columns == [
        {"txt": str, "num": float, "int": int, "rl": float, "blb": bytes},
        {"txt": str, "num": float, "int": int, "rl": float, "blb": bytes},
    ]
