import pathlib
from typing import List, TypeVar

import sqlalchemy as sa
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm import Session


# adapted from @maf88's comment on:
# https://stackoverflow.com/a/58541858
PathLike = TypeVar("PathLike", str, pathlib.Path, None)
ValueTypes = TypeVar("ValueTypes", int, str, float)


def load_db(path: str | PathLike) -> Engine:
    """Returns a connection to the SQLite database

    Args:
        path (str | PathLike): the path to the database file

    Returns:
        Engine: a connection to the database
    """
    return sa.create_engine(f"sqlite:///{path}", echo=True)


def inspect(db: Engine) -> dict:
    """Inspects the given database and returns a dict of information about each
    table in the database. Each key in the dict contains a list of dicts with
    information about each column in the table such as its name, type, and if
    it's a primary key or not.

    Args:
        db (Engine): connection to the database

    Returns:
        dict: top-level keys are the table names with the values as list of dicts
        of information of each column in the table. E.g.,

            {
                "table1": [
                    {
                        "name": "id",
                        "type": Integer,
                        "primary_key": True,
                    },
                    ...
                ],
                "table2": [...],
                ...
            }
    """
    type_map = {
        "INTEGER": sa.Integer,
        "NULL": None,
        "REAL": sa.Float,
        "NUMERIC": sa.Float,
        "TEXT": sa.Text,
        "BLOB": sa.LargeBinary,
    }
    insp = sa.inspect(db)
    columns = {
        table: [
            {
                "name": col["name"],
                "type": type_map[str(col["type"])],
                "primary_key": bool(col["primary_key"]),
            }
            for col in insp.get_columns(table)
        ]
        for table in insp.get_table_names()
    }
    return columns


class Models:
    def __init__(self, engine: Engine) -> None:
        self._models = self._generate_models(engine)

    def _generate_models(self, engine: Engine) -> list:
        """Generates the models for each table in the given database

        Returns:
            list: list of SQLAlchemy models
        """
        insp = inspect(engine)
        table_names = list(insp.keys())
        Base = automap_base()
        Base.prepare(autoload_with=engine, reflect=True)

        return {
            table_name: getattr(Base.classes, table_name) for table_name in table_names
        }

    @property
    def models(self) -> dict:
        return self._models

    def __iter__(self) -> DeclarativeMeta:
        for model in self._models.values():
            yield model

    def __getitem__(self, key):
        return self._models[key]


class QueryValidator:
    """Very basic SQLite query validator."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._info = inspect(engine)

    def validate_params(
        self,
        table: str,
        column: str = None,
        conditional: str = None,
        value: ValueTypes = None,
        ignore_type: bool = True,
    ) -> bool:
        """Validate the params for the SQLite query

        Args:
            params (Iterable): the params to sanitize

        Returns:
            bool: True if params are valid, False otherwise
        """
        is_valid = self._validate_query_params(table, column, conditional, value)
        if not ignore_type:
            is_valid = is_valid and self._validate_value_type(None)

        return is_valid

    def _validate_table(self, table: str) -> bool:
        table_names = list(self._info)
        return table in table_names

    def _validate_column(self, table: str, column: str) -> bool:
        column_names = [col["name"] for col in self._info[table]]
        return column in column_names

    def _validate_conditional(self, conditional: str) -> bool:
        return conditional in ["=", "<", ">", "<>", "<=", ">=", "!="]

    def _validate_query_params(
        self,
        table: str,
        column: str = None,
        conditional: str = None,
        value: ValueTypes = None,
    ) -> bool:

        if not self._validate_table(table):
            return False

        if conditional or value or column:
            # if one of the above is present, then all need to be present
            if not (conditional and value and column):
                return False

            if not self._validate_column(table, column):
                return False

            if not self._validate_conditional(conditional):
                return False

        return True

    def _validate_value_type(self, type_: ValueTypes) -> bool:
        raise NotImplemented()


class Query:
    """Object to query the database.

    NOTE: currently only supports the R in CRUD
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._models = Models(engine)
        self._validator = QueryValidator(engine)

    def create(self):
        raise NotImplementedError()

    def read(
        self,
        table: str,
        column: str = None,
        conditional: str = None,
        value: ValueTypes = None,
    ) -> List:
        """Runs a select statement on the given table based on the given
        conditions (i.e., puts the R in CRUD). If you want all data points,
        then only set the `table` argument. Otherwise, you'll need to use all
        arguments.

        Args:
            table (str): the name of the table
            col (str): (optional) the column to
            conditional (str): (optional) the comparison operator to be used
            from this set of values: ["=", "<", ">", "<>", "<=", ">="]
            value (ValueTypes): (optional) the value to compare to (acceptable
            types are int str, or float)

        Returns:
            Lists: returns a read query
        """

        if not self._validator.validate_params(table, column, conditional, value):
            raise InvalidQueryError("Invalid query.")

        Model = self._models[table]
        with Session(self._engine) as session:
            if column and conditional and value:
                if isinstance(value, str):
                    value = f"'{value}'"
                condition = sa.text(f"{getattr(Model, column)} {conditional} {value}")
                statement = sa.select(Model).where(condition)
            else:
                statement = sa.select(Model)

        return [res[0] for res in session.execute(statement).all()]

    def update(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()


class InvalidQueryError(Exception):
    pass
