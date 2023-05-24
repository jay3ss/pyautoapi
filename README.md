# PyAutoAPI

Give it your database and it gives you an API with an endpoint for each column in
each table (don't worry, you can exclude whatever table/column you like).

***WARNING***: there's absolutely ***no*** security whatsoever. ***Don't*** use
this in production. This should only be used to explore a database or to play
around. If you use it for anything else then that is on ***YOU***.

## Motivation

I was working on a project and needed a way to easily spin up an API. The project
has long since finished, but I had to scratch that itch.

## How to Use

### Requirements

*NOTE*: This is being developed against Python 3.10.8, so it'll work for that
version. Anything else, you're on your own.


It's pretty simple to use. Create a file, import and instantiate a `PyAutoAPI`
object, then run `uvicorn`. That's it! Then you can start querying the API.

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

#### Interacting with the API

Everything is accessed through `/?statement=<my-statement>` endpoint. For example,
if you want to get everything from the table called `users` you'd use the following
query

```python
import json
from urllib import request
from urllib.parse import urlencode

url = f"http://localhost:8000/?{urlencode({'statement': 'select * from users'})}"
response = request.urlopen(url)
data = json.loads(response.read())
```

The `data` variable will hold the results of executing the givens statement and
will always be a `list` of `dict`s. If the execution of the statement was *successful*,
there are two possiblities for the response, the response will contain:

1. the data that you selected if you sent a `SELECT`
   statement as a `list` of `dict`s with each `dict` representing a row
2. a `list` with one `dict`: `[{"info": "Statement executed successfully"}]`
   which happens when a `DELETE`, `INSERT`, or `UPDATE` statement is sent (nothing
   is returned from SQLAlchemy when these statements are executed).

If for some reason the execution of the statement fails, then the following will be
returned:

```python
{
    "detail": "Invalid statement {exception}"
}
```

where `{exception}` contains the exception that SQLAlchemy raised (which includes the
statement that you used) and an `HTTPError` exception will be raised (if using Python
to make the request). For example, if you attempted to `select` from a non-existent
table called `table` then this would be what's returned:

```json
{
  "detail": "Invalid statement: (sqlite3.OperationalError) near \"table\": syntax error\n[SQL: select * from table]\n(Background on this error at: https://sqlalche.me/e/20/e3q8)"
}
```

SQLAlchemy is used to execute the statements that you send as raw `text` statements
so go ahead and use much more complicated statements. Nothing is off limits! This
includes, but is not limited to, SQL injection. Just remember that there's no absolutely
security so if you open this API to the world then you will probably open yourself to
a world of hurt!

### Configuration

You can configure both the FastAPI object that PyAutoAPI uses by passing keyword arguments
when instantiating the PyAutoAPI object or the SQLAlchemy `sessionmaker` function that
PyAutoAPI uses. Here's how:

```python
api = PyAutoAPI() # include any keyword arguments that FastAPI uses
api.init_api(database=database) # include any keyword arguments that sessionmaker uses
```

Make sure that if you want to configure the session that PyAutoAPI uses you must use
the above two-step process and *don't* pass a URL or `Engine` object to the
initializer because that is what triggers the session to be created. If you want to
configure the `Engine` object then create your own with your own configurations and
then pass that to the PyAutoAPI during instantiation or to the `init_api` method.

## Contribution

If you'd like to contribute (this would be very much welcome), then simply fork the repo,
make your changes, and issue a pull request. To install this for development, you'll
need to install the development dependencies using

```bash
make dev-setup
```

You can run the tests with

```bash
make test
```

and for the code coverage report

```bash
make coverage
```

Make sure to format and lint your code with

```bash
make lint
make format
```

respectively.

Certainly! Here's an updated version of the warning section that includes security vulnerabilities:

## Warning: Security Considerations

***IMPORTANT***: PyAutoAPI is intended for **development and exploration purposes only**. It is **not suitable for production environments**. The following points highlight security vulnerabilities that you should be aware of:

1. **No Authentication or Authorization**: PyAutoAPI does not provide any authentication or authorization mechanisms. This means that anyone with access to the API can execute arbitrary SQL statements on the connected database. It is **strongly recommended** to use PyAutoAPI only in isolated and trusted environments.

2. **SQL Injection**: PyAutoAPI executes raw SQL statements provided by users without any sanitization or parameterization. This opens the possibility of SQL injection attacks. **Do not expose the PyAutoAPI endpoint to untrusted or public networks**. Always validate and sanitize user input before constructing SQL statements.

3. **Limited Error Handling**: PyAutoAPI provides minimal error handling and exception reporting. When an error occurs during the execution of a statement, the API response may leak sensitive information, including the SQL statement and underlying database errors. Carefully review and handle exceptions to prevent exposing sensitive information to users.

4. **No Input Validation**: PyAutoAPI does not validate or enforce any constraints on the input statements. This means that malformed or invalid statements could potentially cause unexpected behavior, expose sensitive data, or even lead to database corruption. Always ensure that the input statements are valid and adhere to the expected syntax and semantics.

5. **Potential Denial of Service (DoS) Attacks**: Since PyAutoAPI allows users to execute arbitrary SQL statements, it is possible for malicious users to craft resource-intensive or inefficient queries that could consume excessive system resources and impact the performance of the server. Limit access to PyAutoAPI and monitor resource usage to mitigate potential DoS attacks.

It is crucial to emphasize that PyAutoAPI does not prioritize security features, and using it in an unsecured manner can expose your system to various risks. Always exercise caution and follow secure coding practices when using PyAutoAPI.

Remember, by using PyAutoAPI, you assume all risks and responsibilities. The project's creator and contributors are not liable for any misuse, security breaches, or consequences resulting from using PyAutoAPI in inappropriate or insecure contexts.

## License

This project is licensed under the [MIT License](LICENSE), so basically do whatever the
hell you want to do with this, just don't hold me responsible for whatever terrible
things may happen to you due to the complete lack of security that was mentioned (but not
limited to) above.