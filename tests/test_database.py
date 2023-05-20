import pyautoapi.database as db


def test_inspect_finds_tables(connection):
    inspect = db.inspect(connection)
    assert list(inspect.keys()) == ["table1", "table2"]


def test_inspect_finds_column_names(connection):
    inspect = db.inspect(connection)
    for columns in inspect.values():
        assert [c["name"] for c in columns] == ["id", "txt", "num", "int", "rl", "blb"]


def test_inspect_finds_primary_key(connection):
    inspect = db.inspect(connection)
    for columns in inspect.values():
        for column in columns:
            if column["name"] == "id":
                assert column["primary_key"]
            else:
                assert not column["primary_key"]


def test_query_validator_correct_params(connection):
    qv = db.QueryValidator(connection)
    assert qv.validate_params("table1")
    # "=", "<", ">", "<>", "<=", ">=", "!="
    assert qv.validate_params("table1", "txt", "=", "interpolate")
    assert qv.validate_params("table1", "txt", "<", "interpolate")
    assert qv.validate_params("table1", "txt", ">", "interpolate")
    assert qv.validate_params("table1", "txt", "<>", "interpolate")
    assert qv.validate_params("table1", "txt", "<=", "interpolate")
    assert qv.validate_params("table1", "txt", ">=", "interpolate")
    assert qv.validate_params("table1", "txt", "!=", "interpolate")


def test_query_validator_missing_params(connection):
    qv = db.QueryValidator(connection)
    assert not qv.validate_params({})

    # should have column, conditional, and value (if one is present, all should be)
    assert not qv.validate_params("table1", "txt")
    assert not qv.validate_params("table1", "txt", "=")
    assert not qv.validate_params("table1", "txt", value="interpolate")

    assert not qv.validate_params("table1", conditional="=")
    assert not qv.validate_params("table1", conditional="=", column="txt")
    assert not qv.validate_params("table1", conditional="=", value="interpolate")


def test_query_non_existent_table(connection):
    qv = db.QueryValidator(connection)

    # non-existent table
    assert not qv.validate_params("this_table_doesn't_exist")


def test_query_non_existent_column(connection):
    qv = db.QueryValidator(connection)

    # non-existent column
    assert not qv.validate_params("table1", "col_doesn't_exist", "!=", "interpolate")


def test_query_incorrect_conditional(connection):
    qv = db.QueryValidator(connection)
    assert not qv.validate_params(
        "table1", "col_doesn't_exist", "incorrect", "interpolate"
    )


def test_models(connection):
    ms = db.Models(connection)
    assert list(ms.models.keys()) == ["table1", "table2"]
    columns = ["id", "txt", "rl", "blb", "num", "int"]
    for m in ms:
        for column in columns:
            assert hasattr(m, column)

    assert ms["table1"]
    assert ms["table2"]


def test_query(connection):
    q = db.Query(connection)
    assert len(q.read("table1")) == 100
    assert len(q.read("table2")) == 100
    assert len(q.read("table1", "id", "<", 50)) == 50
    assert len(q.read("table1", "id", "<", 1)) == 1
    result = q.read("table1", "id", "=", 1)[0]
    assert result.id == 1
