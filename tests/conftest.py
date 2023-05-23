import pathlib

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from pyautoapi import PyAutoAPI
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db_path() -> str:
    return "sqlite:///:memory:"


# Create a test database and populate with data
@pytest.fixture(scope="session")
def test_database(test_db_path):
    # Create an in-memory SQLite database
    engine = sa.create_engine(test_db_path)
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


@pytest.fixture(scope="module")
def api_client(test_db_path):
    # Create a test client for the API
    api = PyAutoAPI()
    api.init_api(test_db_path)
    client = TestClient(app=api)

    yield client