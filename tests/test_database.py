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


def test_query_validator_correct_params(load_db):
    qv = db.QueryValidator(load_db)
    assert qv.validate_params({"table": "table1"})
    # "=", "<", ">", "<>", "<=", ">=", "!="
    params = {"table": "table1", "column": "txt", "conditional": "=", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": "<", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": ">", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": "<>", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": "<=", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": ">=", "value": "interpolate"}
    assert qv.validate_params(params)
    params = {"table": "table1", "column": "txt", "conditional": "!=", "value": "interpolate"}
    assert qv.validate_params(params)


def test_query_validator_missing_params(load_db):
    qv = db.QueryValidator(load_db)
    assert not qv.validate_params({})

    # should have column, conditional, and value (if one is present, all should be)
    assert not qv.validate_params({"column": "txt"})
    assert not qv.validate_params({"conditional": "="})
    assert not qv.validate_params({"value": "interpolate"})

    assert not qv.validate_params({"table": "table1", "column": "txt"})
    assert not qv.validate_params({"table": "table1", "column": "txt", "conditional": "="})
    assert not qv.validate_params({"table": "table1", "column": "txt", "value": "interpolate"})

    assert not qv.validate_params({"table": "table1", "conditional": "="})
    assert not qv.validate_params({"table": "table1", "conditional": "=", "column": "txt"})
    assert not qv.validate_params({"table": "table1", "conditional": "=", "value": "interpolate"})


def test_query_non_existent_table(load_db):
    qv = db.QueryValidator(load_db)

    # non-existent table
    assert not qv.validate_params({"table": "this_table_doesn't_exist"})


def test_query_non_existent_column(load_db):
    qv = db.QueryValidator(load_db)

    # non-existent table
    assert not qv.validate_params({"table": "table1", "column": "col_doesn't_exist", "conditional": "!=", "value": "interpolate"})


def test_query_incorrect_conditional(load_db):
    qv = db.QueryValidator(load_db)

    # non-existent table
    assert not qv.validate_params({"table": "table1", "column": "col_doesn't_exist", "conditional": "incorrect", "value": "interpolate"})
