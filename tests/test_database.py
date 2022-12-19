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
    assert qv.validate_params("table1")
    # "=", "<", ">", "<>", "<=", ">=", "!="
    assert qv.validate_params("table1", "txt",  "=", "interpolate")
    assert qv.validate_params("table1", "txt",  "<", "interpolate")
    assert qv.validate_params("table1", "txt",  ">", "interpolate")
    assert qv.validate_params("table1", "txt",  "<>", "interpolate")
    assert qv.validate_params("table1", "txt",  "<=", "interpolate")
    assert qv.validate_params("table1", "txt",  ">=", "interpolate")
    assert qv.validate_params("table1", "txt",  "!=", "interpolate")


def test_query_validator_missing_params(load_db):
    qv = db.QueryValidator(load_db)
    assert not qv.validate_params({})

    # should have column, conditional, and value (if one is present, all should be)
    assert not qv.validate_params("txt")
    assert not qv.validate_params( "=")
    assert not qv.validate_params( "interpolate")

    assert not qv.validate_params("table1", "txt")
    assert not qv.validate_params("table1", "txt",  "=")
    assert not qv.validate_params("table1", "txt",  "interpolate")

    assert not qv.validate_params( "table1", "=")
    assert not qv.validate_params( "table1", "=", "txt")
    assert not qv.validate_params( "table1", "=", "interpolate")


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


def test_models(load_db):
    ms = db.Models(load_db)
    assert list(ms.models.keys()) == ["table1", "table2"]
    columns = ["id", "txt", "rl", "blb", "num", "int"]
    for m in ms:
        for column in columns:
            assert hasattr(m, column)

    assert ms["table1"]
    assert ms["table2"]


def test_query(load_db):
    q = db.Query(load_db)
    assert len(q.read("table1")) == 100
    assert len(q.read("table2")) == 100
    assert len(q.read("table1", "id", "<", 50)) == 50
    assert len(q.read("table1", "id", "<", 1)) == 1
    result = q.read("table1", "id", "=", 1)[0]
    assert result.id == 1



if __name__ == "__main__":
    path = pathlib.Path(__file__).parent/"data/test.db"
    q = db.Query(create_engine(f"sqlite:///{path}"))
    assert len(q.read("table1")) == 100
    assert len(q.read("table2")) == 100