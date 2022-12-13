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
