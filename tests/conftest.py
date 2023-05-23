import pathlib

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from pyautoapi import PyAutoAPI
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def db_string_url(tmp_path_factory):
    return tmp_path_factory.mktemp("test").joinpath("test.db")


# Create a test database and populate with data
@pytest.fixture(scope="session")
def test_database(tmp_path_factory):
    # Create an in-memory SQLite database
    db_path = tmp_path_factory.mktemp("test").joinpath("test.db")
    engine = sa.create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Run SQL scripts to create and populate tables
    data_dir = pathlib.Path(__file__).parent / "data"
    with open(data_dir / "create_tables.sql", "r") as f:
        create_tables_script = f.read().split(";")
        for statement in create_tables_script:
            session.execute(sa.text(statement))

    with open(data_dir / "populate_data.sql", "r") as f:
        populate_data_script = f.read().split(";")
        for statement in populate_data_script:
            session.execute(sa.text(statement + ";"))

    session.commit()
    session.close()

    # Return the database engine
    yield engine

    # Clean up the database
    engine.dispose()


@pytest.fixture(scope="session")
def api_client(test_database):
    # Create a test client for the API
    api = PyAutoAPI()
    api.init_api(test_database)
    client = TestClient(app=api)

    yield client
