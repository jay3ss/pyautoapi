import uvicorn

import pyautoapi as pyapi
from create_db import create_test_database


test_db = ":memory:"
create_test_database(test_db)

api = pyapi.PyAutoAPI(test_db)
uvicorn.run(api, port=5555)
