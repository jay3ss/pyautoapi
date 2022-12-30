# PyAutoAPI

Give it your database and it gives you an API with an endpoint for each column in
each table (don't worry, you can exclude whatever table/column you like).

## How to Use

### Requirements

*NOTE*: This is being developed against Python 3.10.8, so it'll work for that
version. Anything else, you're on your own.


It's pretty simple to use. Create a file, import and instantiate a `pyautoapi.API`
object, then run `uvicorn`. That's it!

### Example

Let's create a file called `main.py` with the following contents

```python
import pyautoapi as pyapi


api = pyapi.PyAutoAPI("mydatabase.db")
```

In your terminal run

```bash
$ uvicorn main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

(If the above terminal looks familiar, it's because `PyAutoAPI` uses `FastAPI`
under the hood.)

Now navigate to [localhost:8000/docs](http://localhost:8000/docs) to see the
Swagger UI.
