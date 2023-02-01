🗄 Credentials Manager
======================

**The credentials managers allows you to store your credentials in your own way.**

meapi, needs to store your credentials (access token, refresh token etc.) in order to be able to use them later on without the need to login again every time you want to use the API.

There are number of credentials managers that are already implemented in the project:

- :py:obj:`~meapi.credentials_managers.json_files.JsonCredentialsManager`: stores the credentials in a json file (``meapi_credentials.json`` by default).
    - This is the default credentials manager.
- :py:obj:`~meapi.credentials_managers.memory.MemoryCredentialsManager`: stores the credentials in memory.
    - The credentials will be lost when the program exits

And more... (see the list below)

---------------------------------

How to use a credentials manager? simple as that:

>>> from me import Me
>>> me = Me(phone_number=972123456789, credentials_manager=YourCredentialsManager())

* You are more than welcome to create your own credentials manager and open a pull request to add it to the project.

---------------------------------

➕ Creating your own custom CredentialsManager
-----------------------------------------------

- You must implement the methods ``get``, ``set``, ``update`` and ``delete`` in order to allow ``meapi`` to store and manage the credentials.

.. currentmodule:: meapi.credentials_managers
.. autoclass:: CredentialsManager()
    :members:
    :undoc-members:

---------------------------------

🗄️ Example: Using a database
----------------------------

Let's say you want to store the credentials in a database

- In this example we will use the `Pony ORM <https://ponyorm.org/>`_ , but you can use any other ORM or database library you want.

Creating the database
......................

First, we need to create the database and the table that will store the credentials:

.. code-block:: python

    from pony.orm import Database, PrimaryKey, Required

    db = Database()
    db.bind(provider='sqlite', filename='meapi_credentials.sqlite', create_db=True)

    class MeUser(db.Entity):
        _table_ = 'me_user'
        phone_number = PrimaryKey(str)
        pwd_token = Required(str)
        access = Required(str)
        refresh = Required(str)
        status = Required(str, default='active')

    db.generate_mapping(create_tables=True)


Implementing the CredentialsManager interface
...............................................

Create a new class that implements the :py:obj:`~meapi.credentials_managers.CredentialsManager` interface:

.. code-block:: python

    from meapi.credentials_manager import CredentialsManager
    from typing import Optional, Dict
    from pony.orm import db_session

    class DatabaseCredentialsManager(CredentialsManager):
        @db_session
        def set(self, phone_number: str, data: dict):
            User(phone_number=phone_number, **data)

        @db_session
        def get(self, phone_number: str) -> Optional[Dict[str, str]]:
            user = User.get(phone_number=phone_number)
            return user.to_dict(only=['pwd_token', 'access', 'refresh']) if
                (user and user.status == 'active') else None

        @db_session
        def update(self, phone_number: str, access_token: str):
            User[phone_number].access = access_token

        @db_session
        def delete(self, phone_number: str):
            User[phone_number].status = 'inactive' # We don't want actually to delete the user from the database


Using the CredentialsManager
............................

Now we can use the credentials manager by passing it to the :py:obj:`~meapi.Me` class:

    >>> from meapi import Me
    >>> dbcm = DatabaseCredentialsManager()
    >>> me = Me(phone_number=972123456789, activation_code='123456', credentials_manager=dbcm)


====================================================================================================

🎛️ Available Credentials Managers
---------------------------------


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