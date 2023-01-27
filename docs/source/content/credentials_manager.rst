🗄 Credentials Manager
======================

**The credentials managers allows you to store your credentials in your own way.**

meapi, needs to store your credentials (access token, refresh token etc.) in order to be able to use them later on without the need to login again every time you want to use the API.

There are number of credentials managers that are already implemented in the project:

- :py:obj:`~meapi.credentials_managers.json_files.JsonCredentialsManager` that stores the credentials in a json file (``meapi_credentials.json`` by default).
    - This is the default credentials manager.
- :py:obj:`~meapi.credentials_managers.memory.MemoryCredentialsManager` that stores the credentials in memory.
    - The credentials will be lost when the program exits
- :py:obj:`~meapi.credentials_managers.redis.RedisCredentialsManager` that stores the credentials in a redis database.
- :py:obj:`~meapi.credentials_managers.flask.FlaskSessionCredentialsManager` that stores the credentials in a flask session.
- :py:obj:`~meapi.credentials_managers.django.DjangoSessionCredentialsManager` that stores the credentials in a django session.

>>> from me import Me
>>> me = Me(phone_number=972123456789, credentials_manager=YourCredentialsManager())

* You are more than welcome to create your own credentials manager and open a pull request to add it to the project.

---------------------------------

➕ **Creating your own custom CredentialsManager:**

- You must implement the methods ``get``, ``set``, ``update`` and ``delete`` in order to allow ``meapi`` to store and manage the credentials.

.. currentmodule:: meapi.credentials_managers
.. autoclass:: CredentialsManager()
    :members:
    :undoc-members:

---------------------------------

📄 **Examples:**

Let's say you want to store the credentials in a database, create a new class that implements the :py:obj:`~meapi.credentials_managers.CredentialsManager` interface:

*In this example we will use the pony ORM, but you can use any other ORM or database library you want.*

.. code-block:: python

    from meapi.credentials_manager import CredentialsManager
    from typing import Optional
    from pony.orm import Database, Required, db_session

    db = Database()

    class User(db.Entity):
        phone_number = Required(str, unique=True)
        pwd_token Required(str)
        access = Required(str)
        refresh = Required(str)

    db.bind(provider='sqlite', filename='meapi_credentials.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)

    # Now we implement the CredentialsManager interface

    class DatabaseCredentialsManager(CredentialsManager):
        def __init__(self):
            pass

        @db_session
        def get(self, phone_number: str) -> Optional[Dict[str, str]]:
            user = User.get(phone_number=phone_number)
            if user:
                return {
                    'pwd_token': user.pwd_token,
                    'access': user.access,
                    'refresh': user.refresh
                }
            return None

        @db_session
        def set(self, phone_number: str, data: dict):
            User(phone_number=phone_number, **data)

        @db_session
        def update(self, phone_number: str, access_token: str):
            User.get(phone_number=phone_number).access = access_token

        @db_session
        def delete(self, phone_number: str):
            User.get(phone_number=phone_number).delete()


You can use the credentials manager in the following way:

    >>> from me import Me
    >>> dbcm = DatabaseCredentialsManager()
    >>> me = Me(phone_number=972123456789, credentials_manager=dbcm)


====================================================================================================

.. currentmodule:: meapi.credentials_managers.json_files
.. autoclass:: JsonCredentialsManager()
.. currentmodule:: meapi.credentials_managers.memory
.. autoclass:: MemoryCredentialsManager()
.. currentmodule:: meapi.credentials_managers.redis
.. autoclass:: RedisCredentialsManager()
.. currentmodule:: meapi.credentials_managers.flask
.. autoclass:: FlaskSessionCredentialsManager()
.. currentmodule:: meapi.credentials_managers.django
.. autoclass:: DjangoSessionCredentialsManager()