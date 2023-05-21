"""
Example script. To run it, from the root of the directory run

uvicorn examples.example:api --port <port>

where <port> is your desired port. If you want to run it on the default port
(8000) then omit the port flag.
"""

import pathlib

import uvicorn

import pyautoapi as pyapi
from .create_db import create_test_database


test_db = "test.db"
if not pathlib.Path(test_db).exists():
    create_test_database(test_db)

api = pyapi.PyAutoAPI(test_db)


if __name__ == "__main__":
    uvicorn.run(f"{pathlib.Path(__file__).stem}:api", port=5555, reload=True)
