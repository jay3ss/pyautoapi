"""
Example script. To run it, from the root of the directory run

uvicorn examples.example:api --port <port>

where <port> is your desired port. If you want to run it on the default port
(8000) then omit the port flag.
"""

import pathlib

import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pyautoapi as pyapi
from create_db import create_test_database


api = pyapi.PyAutoAPI(debug=True)


if __name__ == "__main__":
    test_db = "test.db"
    db_path = pathlib.Path(__file__).parent.parent / test_db
    if not db_path.exists():
        create_test_database(test_db)

    url = f'sqlite:///{str(db_path)}'

    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        api.init_api(session=session)
        uvicorn.run(f"{pathlib.Path(__file__).stem}:api", port=5555, reload=True)
